#!/usr/bin/env node
// seed_month_cycle.mjs
//
// One-hour simulated month for QA: an LLM fabricates the theme, workshop,
// modules, prompts, participants, and per-week responses; this script drives
// the mtc3portal API in the right order so the cycle scheduler can run end-to-end
// and surface AI output for manual review against the rubric in
// `ai_testing_methodology.md`.
//
// Run:
//   node test_cases/scripts/seed_month_cycle.mjs                  # full simulation
//   node test_cases/scripts/seed_month_cycle.mjs --dry-run        # generate but do not POST
//   node test_cases/scripts/seed_month_cycle.mjs --teardown <id>  # remove a previous run
//
// See test_cases/scripts/README.md for the runbook.

import { writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { ApiClient } from "./lib/api.mjs";
import { OpenAIClient } from "./lib/openai.mjs";
import {
  themeSchemaDescription, validateTheme,
  participantsSchemaDescription, validateParticipants,
  formDataValidatorByTemplate, describeFormDataShape,
  buildResponseShapeHint,
} from "./lib/schemas.mjs";

// ──────────────────────────────────────────────────────────────────
// CONFIGURATION — edit defaults here, or override per-call from the CLI.
// ──────────────────────────────────────────────────────────────────
const CONFIG = {
  apiBaseUrl: process.env.MTC3_API_URL || "http://localhost:3036/api",
  openaiApiKey: process.env.OPENAI_API_KEY,
  openaiModel: process.env.OPENAI_MODEL || "gpt-4.1-mini",

  // Shared OpenAI defaults; each call may override individual fields.
  openaiDefaults: {
    temperature: 0.7,
    top_p: 1.0,
    presence_penalty: 0.0,
    frequency_penalty: 0.0,
    max_tokens: 1024,
    seed: 42,
    response_format: { type: "json_object" },
  },

  // Per-call-type overrides — each phase has different needs.
  llmCalls: {
    theme:         { temperature: 0.85, presence_penalty: 0.6, max_tokens: 800 },
    promptContent: { temperature: 0.7,  presence_penalty: 0.4, max_tokens: 1200 },
    participants:  { temperature: 0.6,  frequency_penalty: 0.4, max_tokens: 600 },
    responses:     { temperature: 1.0,  frequency_penalty: 0.7, max_tokens: 400 },
    validation:    { temperature: 0.0,  max_tokens: 256 },
  },

  // Admin credentials. The admin must already exist with `user_type='admin'`
  // (registration cannot create admins). Set via env or hardcode for QA.
  adminEmail: process.env.MTC3_ADMIN_EMAIL || "qa-admin@mtc3.local",
  adminPassword: process.env.MTC3_ADMIN_PASSWORD || "change-me",

  participantCount: 8,
  workshopCount: 1,
  modulesPerWorkshop: 4,         // 4 = one per simulated week
  promptsPerModule: 4,

  // Template-id weighting (1 MC, 3 Checklist, 4 ShortResponse, 6 DnD,
  // 7 SampleRater, 8 Notation, 9 Dropdown). Free-response analysis
  // currently fires on 4, 6, 8 only.
  templateMix: { 4: 0.5, 6: 0.25, 8: 0.15, 1: 0.07, 9: 0.03 },

  // Month-in-an-hour timing. cycleMode='month_in_hour' overrides preset.
  cycleMode: "month_in_hour",     // 'month_in_hour' | 'preset'
  cyclePreset: "extended_test",   // used only when cycleMode='preset'
  monthInHour: {
    totalMinutes: 60,
    weeks: 4,
    openShare: 0.5,               // fraction of each week spent in 'open'
    interCycleBufferSec: 5,
  },

  // Pacing (ms) for participant responses inside the 'open' window.
  pacing: { responseDelayMsMin: 2_000, responseDelayMsMax: 30_000 },

  // Concurrency cap for participant POSTs to avoid hammering the API.
  responseConcurrency: 4,

  // After processing, how long we wait for AI analysis to land.
  aiAwaitTimeoutMs: 5 * 60_000,
  aiAwaitPollMs: 5_000,

  showcaseAtMonthEnd: true,
  dryRun: false,
  verbose: true,
  seed: Number(process.env.MTC3_SEED || 42),
};

// ──────────────────────────────────────────────────────────────────
// Bootstrapping
// ──────────────────────────────────────────────────────────────────
const __dirname = dirname(fileURLToPath(import.meta.url));
const REPORTS_DIR = join(__dirname, "reports");

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) return printHelp();

  if (args.dryRun) CONFIG.dryRun = true;
  if (args.teardown) return runTeardown(args.teardown);

  if (!CONFIG.openaiApiKey) {
    console.error("OPENAI_API_KEY is required (export it before running).");
    process.exit(1);
  }

  const rng = mulberry32(hashString(`${CONFIG.seed}`));
  const api = new ApiClient({
    baseUrl: CONFIG.apiBaseUrl,
    dryRun: CONFIG.dryRun,
    verbose: CONFIG.verbose,
    seed: CONFIG.seed,
  });
  const ai = new OpenAIClient({
    apiKey: CONFIG.openaiApiKey,
    model: CONFIG.openaiModel,
    defaults: CONFIG.openaiDefaults,
    callTypes: CONFIG.llmCalls,
    verbose: CONFIG.verbose,
  });

  const ctx = {
    config: CONFIG,
    rng,
    api,
    ai,
    runId: `seed-${CONFIG.seed}-${Date.now()}`,
    started: new Date().toISOString(),
    entities: {
      adminUserId: null,
      showcaseId: null,
      workshops: [],            // [{ id, name }]
      modules: [],              // [{ workshopId, id, name, weekIndex }]
      prompts: [],              // [{ moduleId, id, templateId, formData }]
      participants: [],         // [{ user_id, email, username, sessionKey }]
    },
  };

  console.log(`[run] starting ${ctx.runId} (dryRun=${CONFIG.dryRun}, mode=${CONFIG.cycleMode})`);

  await bootstrapAdmin(ctx);
  const theme = await generateTheme(ctx);
  await createShowcase(ctx, theme);
  await createWorkshops(ctx, theme);
  await createModules(ctx, theme);
  await generateAndCreatePrompts(ctx, theme);
  await registerParticipants(ctx, theme);
  await runMonthSimulation(ctx, theme);
  await awaitAllAnalysis(ctx);
  await emitTestSessionReport(ctx, theme);

  console.log(`[run] complete: ${ctx.runId}`);
}

// ──────────────────────────────────────────────────────────────────
// Phases
// ──────────────────────────────────────────────────────────────────
async function bootstrapAdmin(ctx) {
  const { api, config } = ctx;
  await api.login("admin", config.adminEmail, config.adminPassword);
  api.use("admin");
}

async function generateTheme(ctx) {
  const { ai, config } = ctx;
  const system = `You are designing the thematic spine of a one-month theater workshop season. You write evocatively and concretely. You never moralize, prescribe, or use evaluative words like "good", "bad", "should", "best".`;
  const user = `Produce JSON exactly matching this shape:
${themeSchemaDescription}

Constraints:
- Workshops: ${config.workshopCount}.
- Modules per workshop: ${config.modulesPerWorkshop} (one per simulated week).
- Each module's subTheme should evolve logically from the previous week.
- Showcase name and description should feel like the destination of the arc.`;

  const theme = await ai.generateJSON({
    callType: "theme",
    system,
    user,
    validate: validateTheme,
  });
  console.log(`[theme] "${theme.title}"`);
  return theme;
}

async function createShowcase(ctx, theme) {
  if (!ctx.config.showcaseAtMonthEnd) return;
  const date = isoDateInDays(28); // ~end of month
  const res = await ctx.api.createShowcase({
    name: theme.showcaseName,
    description: theme.showcaseDescription,
    date,
    location: "MTC3 Studio",
  });
  ctx.entities.showcaseId = res?.showcase_id ?? null;
  console.log(`[showcase] created id=${ctx.entities.showcaseId}`);
}

async function createWorkshops(ctx, theme) {
  for (let i = 0; i < ctx.config.workshopCount; i++) {
    const ws = theme.perWorkshop[i];
    const date = isoDateInDays(7 + i * 7);
    await ctx.api.createWorkshop({
      name: ws.name,
      description: ws.description,
      location: "MTC3 Studio",
      date,
      isPublic: 1,
      showcaseId: ctx.entities.showcaseId,
    });
    // The POST /workshops endpoint doesn't return the new id; look it up
    // by the tagged name.
    const list = await ctx.api.get("/workshops").catch(() => []);
    const tag = ctx.api.tag(ws.name);
    const found = Array.isArray(list)
      ? list.find((w) => typeof w.workshop_name === "string" && w.workshop_name.includes(tag))
      : null;
    if (!found) throw new Error(`couldn't locate created workshop "${ws.name}"`);
    ctx.entities.workshops.push({ id: found.workshop_id, name: ws.name });
    console.log(`[workshop] created id=${found.workshop_id} "${ws.name}"`);
  }
}

async function createModules(ctx, theme) {
  for (let i = 0; i < ctx.config.workshopCount; i++) {
    const ws = ctx.entities.workshops[i];
    const themeWs = theme.perWorkshop[i];
    for (let w = 0; w < ctx.config.modulesPerWorkshop; w++) {
      const m = themeWs.modules[w];
      const id = await ctx.api.createModule(ws.id, m.name);
      ctx.entities.modules.push({ workshopId: ws.id, id, name: m.name, subTheme: m.subTheme, weekIndex: w });
      console.log(`[module] week=${w + 1} workshopId=${ws.id} moduleId=${id} "${m.name}"`);
    }
  }
}

async function generateAndCreatePrompts(ctx, theme) {
  const { ai, api, config, rng } = ctx;
  for (const mod of ctx.entities.modules) {
    const themeWs = theme.perWorkshop.find((_, i) => ctx.entities.workshops[i].id === mod.workshopId);
    const subTheme = mod.subTheme;
    const promptDataList = [];
    for (let p = 0; p < config.promptsPerModule; p++) {
      const templateId = pickWeighted(config.templateMix, rng);
      const formData = await generateFormDataForTemplate(ai, templateId, themeWs.name, subTheme);
      promptDataList.push({ prompt_template_id: templateId, formData });
    }
    await api.createPrompts(mod.workshopId, mod.id, promptDataList);

    // Look up the newly created prompts so we have ids for response submission.
    const fresh = await api.listPrompts(mod.workshopId, mod.id).catch(() => []);
    const sorted = Array.isArray(fresh) ? fresh : [];
    sorted.forEach((row, idx) => {
      const matching = promptDataList[idx];
      if (!matching) return;
      ctx.entities.prompts.push({
        moduleId: mod.id,
        workshopId: mod.workshopId,
        id: row.workshop_prompt_id ?? row.id,
        templateId: matching.prompt_template_id,
        formData: matching.formData,
        weekIndex: mod.weekIndex,
      });
    });
    console.log(`[prompts] module=${mod.id} created=${promptDataList.length}`);
  }
}

async function generateFormDataForTemplate(ai, templateId, workshopName, subTheme) {
  const validator = formDataValidatorByTemplate[templateId];
  const shape = describeFormDataShape(templateId);
  const system = `You are authoring a single prompt for the theater workshop "${workshopName}". The current sub-theme is "${subTheme}". Produce only valid JSON. Do not use evaluative or prescriptive language.`;
  const user = `Return JSON matching:
${shape}

Make the question/items vivid, concrete, and grounded in the sub-theme. Keep options or items between 3 and 6.`;
  return ai.generateJSON({ callType: "promptContent", system, user, validate: validator });
}

async function registerParticipants(ctx, theme) {
  const { ai, api, config } = ctx;
  const system = `You design a small, diverse cohort for a participatory theater workshop. Output only JSON. Names should be plausible; usernames lowercase with no spaces.`;
  const user = `Design ${config.participantCount} participants, returning JSON matching:
${participantsSchemaDescription}

Each persona_hint should be a 2–4 word tag (e.g. "newcomer", "stage manager", "skeptical writer").`;

  const cohort = await ai.generateJSON({
    callType: "participants",
    system,
    user,
    validate: (v) => validateParticipants(v, config.participantCount),
  });

  const password = `QASeed!${config.seed}aA1`;
  for (let i = 0; i < cohort.participants.length; i++) {
    const p = cohort.participants[i];
    const email = `qa-${config.seed}-${i}@mtc3.local`;
    const username = `${p.username}_${config.seed}_${i}`.replace(/\s+/g, "_").toLowerCase();
    if (!(await api.emailExists(email))) {
      await api.registerUser({
        username,
        email,
        first_name: p.first_name,
        last_name: p.last_name,
        user_password: password,
        user_phone: null,
        user_type: "user",
      });
      console.log(`[participant] registered ${username} (${email})`);
    } else {
      console.log(`[participant] ${email} already exists; reusing`);
    }
    const sessionKey = `p${i}`;
    await api.login(sessionKey, email, password);
    const decoded = decodeJwt(api.sessions.get(sessionKey).token);
    ctx.entities.participants.push({
      sessionKey,
      email,
      username,
      first_name: p.first_name,
      last_name: p.last_name,
      persona_hint: p.persona_hint,
      user_id: decoded?.user_id ?? null,
    });
  }
}

async function runMonthSimulation(ctx, theme) {
  const { config, api } = ctx;
  const workshopId = ctx.entities.workshops[0].id;
  const timing = computeTiming(config);
  console.log(`[timing] weekMinutes=${timing.weekMinutes.toFixed(2)}, openHours=${timing.openHours.toFixed(4)}, processingHours=${timing.processingHours.toFixed(4)}`);

  if (config.dryRun) {
    console.log("[dry-run] skipping live cycle starts and response submission");
    return;
  }

  const modulesByWeek = ctx.entities.modules
    .filter((m) => m.workshopId === workshopId)
    .sort((a, b) => a.weekIndex - b.weekIndex);

  for (const mod of modulesByWeek) {
    const week = mod.weekIndex + 1;
    console.log(`\n[week ${week}] ── starting`);

    api.use("admin");
    if (config.cycleMode === "month_in_hour") {
      await api.putCycleConfig(workshopId, {
        preset: "extended_test",
        open_to_processing_hours: timing.openHours,
        processing_to_completed_hours: timing.processingHours,
      });
    } else {
      await api.putCycleConfig(workshopId, { preset: config.cyclePreset });
    }

    // Cancel anything previously scheduled before kicking off this week.
    await api.cancelCycle(workshopId).catch(() => {});
    await api.startCycle(workshopId);

    // Wait for the module to be 'open', then drive responses.
    await waitForModuleStatus(api, workshopId, mod.id, "open", timing.openWaitMs);
    await driveResponsesForModule(ctx, mod, theme, timing);

    // Wait for the module to enter 'processing' (AI fans out here).
    await waitForModuleStatus(api, workshopId, mod.id, "processing", timing.processingWaitMs);
    // And finally 'completed'.
    await waitForModuleStatus(api, workshopId, mod.id, "completed", timing.completedWaitMs);

    await sleep(config.monthInHour.interCycleBufferSec * 1000);
  }
}

async function driveResponsesForModule(ctx, mod, theme, timing) {
  const { ai, api, config, rng } = ctx;
  const prompts = ctx.entities.prompts.filter((p) => p.moduleId === mod.id);
  const participants = ctx.entities.participants;
  // Build a flat queue of (participant, prompt) pairs, shuffled, with pacing.
  const queue = [];
  for (const participant of participants) {
    for (const prompt of prompts) {
      queue.push({ participant, prompt });
    }
  }
  shuffle(queue, rng);

  const concurrency = Math.max(1, config.responseConcurrency);
  let nextIndex = 0;
  const workers = Array.from({ length: concurrency }, async () => {
    while (true) {
      const idx = nextIndex++;
      if (idx >= queue.length) return;
      const { participant, prompt } = queue[idx];
      const delay = randInt(rng, config.pacing.responseDelayMsMin, config.pacing.responseDelayMsMax);
      await sleep(delay);
      try {
        const content = await generateResponseContent(ai, prompt, participant, mod);
        api.use(participant.sessionKey);
        await api.submitResponse({
          workshopId: mod.workshopId,
          moduleId: mod.id,
          promptId: prompt.id,
          templateId: prompt.templateId,
          content,
        });
      } catch (err) {
        console.warn(`[response] participant=${participant.username} prompt=${prompt.id} failed:`, err.message);
      }
    }
  });
  await Promise.all(workers);
  api.use("admin");
  console.log(`[week ${mod.weekIndex + 1}] responses submitted`);
}

async function generateResponseContent(ai, prompt, participant, mod) {
  const shape = buildResponseShapeHint(prompt.templateId, prompt.formData);
  const system = `You are role-playing the participant "${participant.first_name} ${participant.last_name}", described as: ${participant.persona_hint}. You are responding to a workshop prompt under the sub-theme "${mod.subTheme}". Output only JSON in the requested shape. Stay in character; vary your voice from other participants.`;
  const user = `Prompt configuration:
${JSON.stringify(prompt.formData, null, 2)}

Respond with JSON matching:
${shape}

Be vivid and specific. No generic platitudes.`;
  return ai.generateJSON({
    callType: "responses",
    system,
    user,
    // Per-template content shapes are too varied for a strict programmatic
    // validator here — the API server is the authority and will reject bad
    // shapes. We rely on JSON-mode + the shape hint.
    validate: undefined,
  });
}

async function awaitAllAnalysis(ctx) {
  const { api, config } = ctx;
  // Only free-response templates are intended to receive AI analysis.
  // (The current backend bug fans out to all templates — see TC-AI-001.)
  const FREE_RESPONSE_TEMPLATES = new Set([4, 6, 8]);
  const targets = ctx.entities.prompts.filter((p) => FREE_RESPONSE_TEMPLATES.has(p.templateId));
  const deadline = Date.now() + config.aiAwaitTimeoutMs;
  const remaining = new Map(targets.map((p) => [p.id, p]));
  while (remaining.size > 0 && Date.now() < deadline) {
    for (const promptId of [...remaining.keys()]) {
      const row = await api.getAiAnalysis(promptId);
      if (row) {
        remaining.delete(promptId);
        console.log(`[ai] analysis ready for prompt=${promptId}`);
      }
    }
    if (remaining.size > 0) await sleep(config.aiAwaitPollMs);
  }
  if (remaining.size > 0) {
    console.warn(`[ai] timed out waiting on ${remaining.size} prompts; report will note 'pending'`);
  }
}

async function emitTestSessionReport(ctx, theme) {
  await mkdir(REPORTS_DIR, { recursive: true });
  const file = join(REPORTS_DIR, `${ctx.runId}.json`);
  const summary = {
    runId: ctx.runId,
    seed: ctx.config.seed,
    started: ctx.started,
    finished: new Date().toISOString(),
    config: redactConfig(ctx.config),
    theme,
    entities: {
      showcaseId: ctx.entities.showcaseId,
      workshops: ctx.entities.workshops,
      modules: ctx.entities.modules,
      prompts: ctx.entities.prompts.map((p) => ({
        id: p.id, moduleId: p.moduleId, templateId: p.templateId, weekIndex: p.weekIndex,
      })),
      participants: ctx.entities.participants.map((p) => ({
        user_id: p.user_id, username: p.username, persona_hint: p.persona_hint,
      })),
    },
    openaiUsage: ctx.ai.usage,
    rubricChecklist: ctx.entities.prompts
      .filter((p) => [4, 6, 8].includes(p.templateId))
      .map((p) => ({
        promptId: p.id, templateId: p.templateId, weekIndex: p.weekIndex,
        rubricFile: "test_cases/ai_testing_methodology.md",
        scoreHere: { faithfulness: null, relevance: null, neutrality: null, coverage: null,
          conciseness: null, format: null, safety: null, welcomingTone: null, senseOfInfluence: null, personaFit: null },
      })),
  };
  await writeFile(file, JSON.stringify(summary, null, 2));
  console.log(`[report] wrote ${file}`);
}

// ──────────────────────────────────────────────────────────────────
// Teardown
// ──────────────────────────────────────────────────────────────────
async function runTeardown(reportFileOrId) {
  const file = reportFileOrId.endsWith(".json")
    ? reportFileOrId
    : join(REPORTS_DIR, `${reportFileOrId}.json`);
  if (!existsSync(file)) {
    console.error(`report not found: ${file}`);
    process.exit(1);
  }
  const report = JSON.parse(await (await import("node:fs/promises")).readFile(file, "utf8"));
  const api = new ApiClient({ baseUrl: CONFIG.apiBaseUrl, verbose: true, seed: report.seed });
  await api.login("admin", CONFIG.adminEmail, CONFIG.adminPassword);
  api.use("admin");
  for (const ws of report.entities.workshops) {
    await api.deleteWorkshop(ws.id).catch((e) => console.warn(`teardown workshop ${ws.id}: ${e.message}`));
  }
  if (report.entities.showcaseId) {
    await api.deleteShowcase(report.entities.showcaseId).catch((e) => console.warn(`teardown showcase: ${e.message}`));
  }
  console.log("[teardown] done. Note: participants and AI analysis rows are not auto-deleted.");
}

// ──────────────────────────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────────────────────────
function computeTiming(config) {
  if (config.cycleMode === "preset") {
    return { weekMinutes: NaN, openHours: NaN, processingHours: NaN, openWaitMs: 60 * 60_000, processingWaitMs: 60 * 60_000, completedWaitMs: 60 * 60_000 };
  }
  const { totalMinutes, weeks, openShare } = config.monthInHour;
  const weekMinutes = totalMinutes / weeks;
  const openHours = (weekMinutes * openShare) / 60;
  const processingHours = (weekMinutes * (1 - openShare)) / 60;
  // Wall-clock ms windows we'll wait for the worker to flip status.
  const openWaitMs = Math.ceil(openHours * 60 * 60_000) + 30_000;
  const processingWaitMs = Math.ceil(processingHours * 60 * 60_000) + 30_000;
  const completedWaitMs = processingWaitMs + 30_000;
  return { weekMinutes, openHours, processingHours, openWaitMs, processingWaitMs, completedWaitMs };
}

async function waitForModuleStatus(api, workshopId, moduleId, target, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const res = await api.getModuleStatus(workshopId, moduleId);
      // Backend returns mysql2 result tuple; status string lives in res[0][0].workshop_module_status.
      const status = extractModuleStatus(res);
      if (status === target) return;
      if (target === "open" && status === "processing") return; // we missed open; that's fine
      if (target === "processing" && status === "completed") return;
    } catch { /* swallow transient errors */ }
    await sleep(2_000);
  }
  console.warn(`[wait] module=${moduleId} did not reach status=${target} within ${timeoutMs}ms`);
}

function extractModuleStatus(res) {
  if (!res) return null;
  if (Array.isArray(res) && Array.isArray(res[0])) return res[0]?.[0]?.workshop_module_status ?? null;
  if (Array.isArray(res)) return res[0]?.workshop_module_status ?? null;
  return res?.workshop_module_status ?? null;
}

function pickWeighted(weightMap, rng) {
  const entries = Object.entries(weightMap).map(([k, v]) => [Number(k), Number(v)]);
  const total = entries.reduce((s, [, w]) => s + w, 0);
  let r = rng() * total;
  for (const [id, w] of entries) {
    r -= w;
    if (r <= 0) return id;
  }
  return entries[entries.length - 1][0];
}

function shuffle(arr, rng) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
}

function randInt(rng, min, max) {
  return Math.floor(min + rng() * (max - min + 1));
}

function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }

function isoDateInDays(days) {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

function decodeJwt(token) {
  try {
    const [, payload] = token.split(".");
    return JSON.parse(Buffer.from(payload, "base64url").toString("utf8"));
  } catch { return null; }
}

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function hashString(s) {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function redactConfig(c) {
  return {
    ...c,
    openaiApiKey: c.openaiApiKey ? "[REDACTED]" : null,
    adminPassword: "[REDACTED]",
  };
}

function parseArgs(argv) {
  const out = { dryRun: false, teardown: null, help: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--dry-run") out.dryRun = true;
    else if (a === "--teardown") out.teardown = argv[++i];
    else if (a === "-h" || a === "--help") out.help = true;
  }
  return out;
}

function printHelp() {
  console.log(`Usage:
  node test_cases/scripts/seed_month_cycle.mjs                  # full simulation
  node test_cases/scripts/seed_month_cycle.mjs --dry-run        # generate but do not POST
  node test_cases/scripts/seed_month_cycle.mjs --teardown <id>  # remove a previous run

Environment:
  MTC3_API_URL          (default http://localhost:3036/api)
  MTC3_ADMIN_EMAIL      admin login email
  MTC3_ADMIN_PASSWORD   admin login password
  MTC3_SEED             integer seed (default 42)
  OPENAI_API_KEY        required
  OPENAI_MODEL          default gpt-4.1-mini

Edit the CONFIG block at the top for advanced tuning (per-call temperature,
template mix, cycle timing, pacing, etc.).
`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
