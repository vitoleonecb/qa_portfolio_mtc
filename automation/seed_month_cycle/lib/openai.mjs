// Thin OpenAI Chat Completions wrapper for the orchestrator.
// - Accepts per-call-type overrides on top of shared defaults.
// - Forces `response_format: { type: 'json_object' }` so we get parseable JSON.
// - Validate-then-re-ask loop: if the parsed object fails the caller's
//   validator, the next attempt switches to the `validation` overrides
//   (low temperature) and includes the validator errors in the user message
//   so the model can self-correct.
// - Tracks aggregate token usage so the orchestrator can put it in its report.

const OPENAI_API_URL = "https://api.openai.com/v1/chat/completions";

export class OpenAIClient {
  constructor({ apiKey, model, defaults = {}, callTypes = {}, verbose = false }) {
    if (!apiKey) throw new Error("OpenAIClient requires apiKey");
    if (!model) throw new Error("OpenAIClient requires model");
    this.apiKey = apiKey;
    this.model = model;
    this.defaults = defaults;
    this.callTypes = callTypes;
    this.verbose = verbose;
    this.usage = { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0, callCount: 0 };
  }

  log(...args) { if (this.verbose) console.log("[openai]", ...args); }

  /** Combine shared defaults with the per-call-type overrides. */
  mergeParams(callType, extra = {}) {
    const overrides = this.callTypes[callType] || {};
    return { ...this.defaults, ...overrides, ...extra };
  }

  /**
   * Generate JSON for a given call type.
   *
   * @param {object} args
   * @param {string} args.callType            'theme' | 'promptContent' | 'participants' | 'responses' | 'validation'
   * @param {string} args.system              system prompt
   * @param {string} args.user                user message
   * @param {(value:any) => {ok:boolean, errors?:string[]}} [args.validate]  optional shape validator
   * @param {number} [args.maxValidationRetries=2]
   */
  async generateJSON({ callType, system, user, validate, maxValidationRetries = 2 }) {
    let attempt = 0;
    let lastErrors = null;
    let lastRaw = null;
    while (attempt <= maxValidationRetries) {
      const useValidationOverrides = attempt > 0;
      const params = this.mergeParams(useValidationOverrides ? "validation" : callType);
      const userMessage = lastErrors
        ? `${user}\n\nYour previous response failed validation:\n- ${lastErrors.join("\n- ")}\nReturn ONLY corrected JSON.`
        : user;

      const raw = await this.completeChat({
        params,
        messages: [
          { role: "system", content: system },
          { role: "user", content: userMessage },
        ],
      });
      lastRaw = raw;

      const parsed = safeParseJSON(raw);
      if (parsed === null) {
        lastErrors = ["response was not valid JSON"];
        attempt += 1;
        continue;
      }

      if (typeof validate === "function") {
        const result = validate(parsed);
        if (result.ok) return result.value ?? parsed;
        lastErrors = result.errors || ["unknown validation error"];
        attempt += 1;
        continue;
      }
      return parsed;
    }
    const err = new Error(`generateJSON(${callType}) failed validation after ${maxValidationRetries + 1} attempts`);
    err.lastErrors = lastErrors;
    err.lastRaw = lastRaw;
    throw err;
  }

  /** Direct call returning the raw assistant text. */
  async completeChat({ params, messages }) {
    const body = {
      model: params.model || this.model,
      messages,
    };
    // Only forward parameters the API understands.
    for (const k of [
      "temperature", "top_p", "presence_penalty", "frequency_penalty",
      "max_tokens", "seed", "response_format",
    ]) {
      if (params[k] !== undefined) body[k] = params[k];
    }
    // Always prefer JSON mode unless caller explicitly opted out.
    if (!body.response_format) body.response_format = { type: "json_object" };

    this.log(`call: model=${body.model}, temp=${body.temperature}, max=${body.max_tokens}`);

    const res = await fetch(OPENAI_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${this.apiKey}` },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      const err = new Error(`OpenAI ${res.status}: ${text}`);
      err.status = res.status;
      throw err;
    }
    const data = await res.json();
    if (data?.usage) {
      this.usage.prompt_tokens += data.usage.prompt_tokens || 0;
      this.usage.completion_tokens += data.usage.completion_tokens || 0;
      this.usage.total_tokens += data.usage.total_tokens || 0;
    }
    this.usage.callCount += 1;
    const content = data?.choices?.[0]?.message?.content;
    if (typeof content !== "string" || !content.trim()) {
      throw new Error("OpenAI returned empty content");
    }
    return content.trim();
  }
}

function safeParseJSON(text) {
  if (!text) return null;
  let cleaned = text.trim();
  // Strip Markdown fences if the model added them despite JSON mode.
  if (cleaned.startsWith("```")) {
    cleaned = cleaned.replace(/^```(?:json)?/i, "").replace(/```$/i, "").trim();
  }
  try { return JSON.parse(cleaned); } catch { return null; }
}
