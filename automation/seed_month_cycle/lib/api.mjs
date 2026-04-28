// HTTP helper for the mtc3portal backend.
// - JWT cache with auto re-login on 401
// - Retry with backoff on 429 / 5xx
// - dryRun mode (logs intended request, returns a stub)
// - Resource-level helpers grouped at the bottom of this file
//
// All entity-creating helpers prepend a `[QA-SEED-<seed>]` tag to names
// so seeded data is unambiguous on a shared dev DB.

const DEFAULT_RETRY = {
  maxAttempts: 4,
  baseDelayMs: 500,
  maxDelayMs: 5000,
};

export class ApiClient {
  constructor({ baseUrl, dryRun = false, verbose = false, seed = 0, retry = DEFAULT_RETRY }) {
    if (!baseUrl) throw new Error("ApiClient requires baseUrl");
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.dryRun = dryRun;
    this.verbose = verbose;
    this.seed = seed;
    this.retry = retry;
    // sessionKey -> { email, password, token }
    this.sessions = new Map();
    this.activeKey = null;
  }

  tag(name) {
    return `[QA-SEED-${this.seed}] ${name}`;
  }

  log(...args) {
    if (this.verbose) console.log("[api]", ...args);
  }

  // ─── Session management ────────────────────────────────────────
  async login(sessionKey, email, password) {
    const res = await this.request("POST", "/users/login", { email, password }, { skipAuth: true });
    if (!res?.accessToken) throw new Error(`login failed for ${email}`);
    this.sessions.set(sessionKey, { email, password, token: res.accessToken });
    this.log(`logged in as ${sessionKey} (${email})`);
    return res;
  }

  use(sessionKey) {
    if (!this.sessions.has(sessionKey)) throw new Error(`unknown session: ${sessionKey}`);
    this.activeKey = sessionKey;
    return this;
  }

  currentToken() {
    return this.activeKey ? this.sessions.get(this.activeKey)?.token : null;
  }

  async refreshActive() {
    if (!this.activeKey) throw new Error("no active session to refresh");
    const s = this.sessions.get(this.activeKey);
    return this.login(this.activeKey, s.email, s.password);
  }

  // ─── Core request with retry + 401 refresh ────────────────────
  async request(method, path, body, opts = {}) {
    const url = `${this.baseUrl}${path}`;
    const init = { method, headers: { "Content-Type": "application/json" } };
    if (body !== undefined && body !== null) init.body = JSON.stringify(body);

    if (!opts.skipAuth) {
      const token = this.currentToken();
      if (token) init.headers.Authorization = `Bearer ${token}`;
    }

    if (this.dryRun && method !== "GET") {
      this.log(`DRY-RUN ${method} ${path}`, redact(body));
      return { ok: true, dryRun: true };
    }

    let attempt = 0;
    let lastError;
    while (attempt < this.retry.maxAttempts) {
      attempt += 1;
      try {
        const res = await fetch(url, init);
        if (res.status === 401 && !opts.skipAuth && !opts._didRefresh) {
          this.log(`401 on ${method} ${path}; refreshing token`);
          await this.refreshActive();
          init.headers.Authorization = `Bearer ${this.currentToken()}`;
          opts._didRefresh = true;
          continue;
        }
        if (res.status === 429 || res.status >= 500) {
          const delay = backoffDelay(attempt, this.retry);
          this.log(`${res.status} on ${method} ${path}; retrying in ${delay}ms`);
          await sleep(delay);
          continue;
        }
        const text = await res.text();
        const parsed = parseMaybeJson(text);
        if (!res.ok) {
          const err = new Error(`${method} ${path} failed: ${res.status} ${typeof parsed === "string" ? parsed : JSON.stringify(parsed)}`);
          err.status = res.status;
          err.body = parsed;
          throw err;
        }
        return parsed;
      } catch (err) {
        lastError = err;
        if (err.status && err.status < 500 && err.status !== 429) throw err;
        const delay = backoffDelay(attempt, this.retry);
        this.log(`error on ${method} ${path}: ${err.message}; retrying in ${delay}ms`);
        await sleep(delay);
      }
    }
    throw lastError || new Error(`request failed after ${this.retry.maxAttempts} attempts`);
  }

  get(path, opts) { return this.request("GET", path, undefined, opts); }
  post(path, body, opts) { return this.request("POST", path, body, opts); }
  put(path, body, opts) { return this.request("PUT", path, body, opts); }
  del(path, opts) { return this.request("DELETE", path, undefined, opts); }

  // ─── User helpers ──────────────────────────────────────────────
  async emailExists(email) {
    try {
      const r = await this.get(`/users/email/${encodeURIComponent(email)}/exists`, { skipAuth: true });
      return !!r?.exists;
    } catch { return false; }
  }

  async registerUser({ username, email, first_name, last_name, user_password, user_phone, user_type = "user", notification_settings = null, avatar_config = null }) {
    return this.post("/users/registration", {
      username, email, first_name, last_name, user_password, user_phone,
      user_type, notification_settings, avatar_config,
    }, { skipAuth: true });
  }

  // ─── Showcase ──────────────────────────────────────────────────
  async createShowcase({ name, description, date, location }) {
    return this.post("/showcases", {
      showcase_name: this.tag(name),
      showcase_description: description,
      showcase_date: date,
      showcase_location: location,
    });
  }

  async deleteShowcase(showcaseId) {
    return this.del(`/showcases/${showcaseId}`);
  }

  // ─── Workshop ──────────────────────────────────────────────────
  async createWorkshop({ name, description, location, date, isPublic = 1, showcaseId = null }) {
    return this.post("/workshops", {
      workshop_name: this.tag(name),
      workshop_description: description,
      workshop_location: location,
      workshop_date: date,
      workshop_public: isPublic,
      showcase_id: showcaseId,
    });
  }

  async deleteWorkshop(workshopId) {
    return this.del(`/workshops/${workshopId}`);
  }

  // ─── Module ────────────────────────────────────────────────────
  async createModule(workshopId, name) {
    // Server returns a 201 text body (`New Module "name" added to workshop id: X`)
    // not JSON, so this helper does its own GET to recover the new module id.
    await this.post(`/workshops/${workshopId}/modules`, {
      workshop_module_name: this.tag(name),
    });
    const list = await this.get(`/workshops/${workshopId}/modules`).catch(() => null);
    if (Array.isArray(list)) {
      const tagged = list.filter((m) => typeof m.workshop_module_name === "string" && m.workshop_module_name.includes(this.tag(name)));
      if (tagged.length > 0) {
        return tagged[tagged.length - 1].workshop_module_id;
      }
    }
    return null; // caller may need to look it up via /cycle/validate/:workshopId
  }

  async deleteModule(workshopId, moduleId) {
    return this.del(`/workshops/${workshopId}/modules/${moduleId}`);
  }

  // ─── Prompts ───────────────────────────────────────────────────
  async createPrompts(workshopId, moduleId, promptDataList) {
    return this.post(`/workshops/${workshopId}/modules/${moduleId}/prompts`, { promptDataList });
  }

  async listPrompts(workshopId, moduleId) {
    return this.get(`/workshops/${workshopId}/modules/${moduleId}/prompts`);
  }

  // ─── Response submission ──────────────────────────────────────
  async submitResponse({ workshopId, moduleId, promptId, templateId, content }) {
    return this.post(`/workshops/${workshopId}/modules/${moduleId}/prompts/${promptId}/response`, {
      workshop_response_content: content,
      prompt_template_id: templateId,
    });
  }

  // ─── Cycle scheduler ──────────────────────────────────────────
  async putCycleConfig(workshopId, { preset = "normal", start_day = 3, start_hour = 7, open_to_processing_hours, processing_to_completed_hours }) {
    const body = { preset, start_day, start_hour };
    if (typeof open_to_processing_hours === "number") body.open_to_processing_hours = open_to_processing_hours;
    if (typeof processing_to_completed_hours === "number") body.processing_to_completed_hours = processing_to_completed_hours;
    return this.put(`/cycle/config/${workshopId}`, body);
  }

  async startCycle(workshopId) {
    return this.post(`/cycle/start/${workshopId}`);
  }

  async cancelCycle(workshopId) {
    return this.post(`/cycle/cancel/${workshopId}`);
  }

  async cycleStatus(workshopId) {
    return this.get(`/cycle/status/${workshopId}`);
  }

  async cycleValidate(workshopId) {
    return this.get(`/cycle/validate/${workshopId}`);
  }

  // ─── Module status (for waiting / polling) ────────────────────
  async modulesProgress(workshopId) {
    return this.get(`/workshops/${workshopId}/modulesprogress`);
  }

  async getModuleStatus(workshopId, moduleId) {
    return this.get(`/workshops/${workshopId}/modules/${moduleId}`);
  }

  // ─── AI analysis ──────────────────────────────────────────────
  async getAiAnalysis(promptId) {
    try {
      return await this.get(`/analytics/ai/${promptId}`);
    } catch (err) {
      if (err.status === 404) return null;
      throw err;
    }
  }
}

// ─── Utilities ─────────────────────────────────────────────────
function backoffDelay(attempt, { baseDelayMs, maxDelayMs }) {
  const exp = Math.min(maxDelayMs, baseDelayMs * 2 ** (attempt - 1));
  // full jitter
  return Math.floor(Math.random() * exp);
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function parseMaybeJson(text) {
  if (!text) return null;
  try { return JSON.parse(text); } catch { return text; }
}

function redact(body) {
  if (!body || typeof body !== "object") return body;
  const out = { ...body };
  for (const k of Object.keys(out)) {
    if (/password|token|secret/i.test(k)) out[k] = "[REDACTED]";
  }
  return out;
}
