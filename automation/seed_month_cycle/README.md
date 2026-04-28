# Month-in-an-Hour Simulation Runbook

`seed_month_cycle.mjs` drives a full simulated month of mtc3portal activity in roughly one hour of wall-clock time. It uses an LLM to fabricate the theme, workshop, modules, prompts, participants, and per-week responses, then drives the real backend API in the order the cycle scheduler expects.

The output is a populated database (workshops, modules, prompts, users, responses) and a JSON report under `reports/` that links each free-response prompt to the rubric in `../ai_testing_methodology.md`. A QA reviewer then evaluates the AI output produced by the live pipeline.

---

## Prerequisites

1. **Backend running.**
   - `cd back_end && npm install && npm run dev`
   - Backend listens on `http://localhost:3036` by default.
   - `.env` in `back_end/` must include `DB_*`, `ACCESS_TOKEN_SECRET`, and `OPENAI_API_KEY` (the backend itself calls OpenAI for AI analysis).
2. **Redis available.** BullMQ workers connect via `ioredis` defaults.
3. **Module worker and AI worker running.**
   - `node back_end/workers/moduleWorker.js`
   - `node back_end/workers/aiAnalysisWorker.js`
   - These two processes are what advance modules through `open → processing → completed` and produce the AI output the simulation is designed to surface.
4. **An admin account already exists** with `user_type='admin'` in the `users` table. Registration cannot create admins. Set `MTC3_ADMIN_EMAIL` / `MTC3_ADMIN_PASSWORD` to those credentials.
5. **OpenAI API key** in your shell: `export OPENAI_API_KEY=sk-...`. The script aborts if this is missing.

---

## Quick start

```bash
# from the repo root
export OPENAI_API_KEY=sk-...
export MTC3_ADMIN_EMAIL=qa-admin@mtc3.local
export MTC3_ADMIN_PASSWORD=...your-password...

# dry run — generates content via OpenAI and logs intended writes, no POSTs
node test_cases/scripts/seed_month_cycle.mjs --dry-run

# real run — drives the API end-to-end, ~60 minutes wall clock
node test_cases/scripts/seed_month_cycle.mjs
```

A run identifier (`seed-<seed>-<timestamp>`) is printed at the start; the matching report lands at `test_cases/scripts/reports/<runId>.json` when finished.

---

## Configuration

All knobs live in the `CONFIG` block at the top of `seed_month_cycle.mjs`. Edit the file directly for non-trivial changes; environment variables cover the most common ones.

### LLM tuning (per call type)

```javascript
openaiDefaults: {
  temperature: 0.7,
  top_p: 1.0,
  presence_penalty: 0.0,
  frequency_penalty: 0.0,
  max_tokens: 1024,
  seed: 42,
  response_format: { type: "json_object" },
},
llmCalls: {
  theme:         { temperature: 0.85, presence_penalty: 0.6, max_tokens: 800 },
  promptContent: { temperature: 0.7,  presence_penalty: 0.4, max_tokens: 1200 },
  participants:  { temperature: 0.6,  frequency_penalty: 0.4, max_tokens: 600 },
  responses:     { temperature: 1.0,  frequency_penalty: 0.7, max_tokens: 400 },
  validation:    { temperature: 0.0,  max_tokens: 256 },
},
```

- `temperature` and `top_p` — randomness. Tune one, not both.
- `presence_penalty` (-2…2) — pushes toward new topics. Useful on `theme`.
- `frequency_penalty` (-2…2) — discourages verbatim repetition. Useful on `participants` and `responses`.
- `max_tokens` — hard cap; the main cost lever.
- `validation` — used automatically when a response fails the JSON validator.

### Time scaling

```javascript
cycleMode: "month_in_hour",
monthInHour: { totalMinutes: 60, weeks: 4, openShare: 0.5, interCycleBufferSec: 5 },
```

Defaults give 4 simulated weeks of 15 min each (≈ 7.5 min open + 7.5 min processing). Change `totalMinutes` or `weeks` to stretch or shrink. To use the backend presets directly, set `cycleMode: "preset"` and choose `cyclePreset`.

### Cohort & content size

- `participantCount` — 8 by default; cost scales linearly.
- `modulesPerWorkshop: 4` — one per simulated week.
- `promptsPerModule: 4` — number of prompts per week.
- `templateMix` — weighting by `prompt_template_id`. Free-response analysis fires only on 4, 6, 8 (per `ai_analysis_test_cases.md` TC-AI-001).

### Seeding & idempotency

- `seed` (env `MTC3_SEED`) drives both deterministic content selection and the email/username scheme (`qa-<seed>-<i>@mtc3.local`).
- Re-running with the same seed reuses participants by checking `GET /users/email/:email/exists`.
- Every entity name is prefixed `[QA-SEED-<seed>]` so seeded data is unambiguous on shared DBs.

---

## Wall-clock expectations

- **Dry run:** 1–3 min (purely LLM calls).
- **Live month-in-an-hour run:** ≈ 60 min, dominated by the four 15-min simulated weeks. Add a couple of minutes for theme + prompt content generation up front and a few minutes at the end while the AI worker drains.
- **Setup (theme, workshops, modules, prompts):** ≈ 1–3 min.
- **Per simulated week:** ≈ 15 min by default, with ~4 sec of LLM-driven response generation per (participant × prompt) pair, capped to `responseConcurrency` parallel workers.

---

## OpenAI cost rough-cut

For default settings (8 participants, 1 workshop, 4 modules, 4 prompts/module):

- **Theme:** 1 call.
- **Prompt content:** 4 modules × 4 prompts = 16 calls.
- **Participants:** 1 call (whole roster at once).
- **Responses:** 8 × 16 = 128 calls.
- **Backend AI analysis:** 4 free-response-style prompts per week × 4 weeks × ~4 LLM calls per prompt (`word_bubbles`, `labels`, `similarities`, `summary`, plus a synthesis) ≈ 80 backend calls — billed to the same key.

Total ~225 OpenAI calls for a default run. Token budget is bounded by `max_tokens` per call type; check the `openaiUsage` block in the report file to confirm actual usage. Set `--dry-run` first when iterating on prompts to avoid burning cost.

---

## Interpreting the report file

`reports/<runId>.json` contains:

- `runId`, `seed`, `started`, `finished`.
- `config` (with secrets redacted).
- `theme` — the LLM-generated thematic spine.
- `entities` — every showcase / workshop / module / prompt / participant the script created. Useful for both teardown and manual lookup.
- `openaiUsage` — `prompt_tokens`, `completion_tokens`, `total_tokens`, `callCount`.
- `rubricChecklist` — one entry per free-response prompt, pre-wired with the rubric dimension fields you'll fill in by hand against `../ai_testing_methodology.md`.

---

## Teardown

```bash
node test_cases/scripts/seed_month_cycle.mjs --teardown <runId>
# or pass an absolute path to the report file
```

The teardown deletes workshops (cascading to modules and prompts) and the showcase. **Participants and AI analysis rows are not deleted** — they're cheap to leave, and they have meaningful audit value if you want to re-trigger analysis on the same prompts later.

---

## Troubleshooting

- **`OPENAI_API_KEY is required`** — export it in your shell.
- **`couldn't locate created workshop`** — the script looks up the new workshop id by its tagged name. If the seed prefix collided with an earlier run, try a new `MTC3_SEED`.
- **AI worker never produces analysis** — confirm `aiAnalysisWorker.js` is running and the backend's `OPENAI_API_KEY` is set. The worker fails soft with empty-shape rows when the key is missing (`aiAnalysisService.js:649-662`); the script's `awaitAllAnalysis` step will still consider those "ready", so check the actual row content.
- **`401` mid-run** — JWTs expire after one hour. The API helper auto-refreshes on 401 by re-calling login; if you see the failure repeat, the password may be wrong.
- **`429` from OpenAI** — the OpenAI client doesn't currently back off; if you hit it, lower `responseConcurrency` or the cohort size.
- **Cycle scheduler rejects start with "Some modules are missing prompts"** — `generateAndCreatePrompts` ran but didn't actually persist any. Confirm the admin token has `user_type='admin'` and the `/prompts` POST returned 201.

---

## Where the rubric lives

After a run, open `../ai_testing_methodology.md`. Use the **Evaluation rubric** section to score each prompt referenced by `rubricChecklist`. Append your scored rows to the **Results table** at the bottom of that file, and fill in a fresh **Missed-opportunity worksheet** per simulated week.
