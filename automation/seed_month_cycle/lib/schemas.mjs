// Lightweight JSON schemas + validators for the orchestrator.
//
// We avoid a heavy dependency like ajv on purpose — every shape here is small,
// and validation feedback feeds directly back into the LLM "validation" call type
// so the model can self-correct.
//
// Each `validate*` function returns either { ok: true, value } or
// { ok: false, errors: string[] } so the OpenAI helper can decide whether to
// re-ask.

// ─── Theme ─────────────────────────────────────────────────────────
// Generated once per simulation. Provides the thematic spine the rest
// of the script borrows from.
export const themeSchemaDescription = `{
  "title": string,                       // short, evocative thematic title
  "season": string,                      // a sentence framing the month
  "perWorkshop": [                       // one entry per workshop
    {
      "name": string,
      "description": string,             // 1–2 sentences
      "modules": [                       // length === modulesPerWorkshop
        { "name": string, "subTheme": string }
      ]
    }
  ],
  "showcaseName": string,
  "showcaseDescription": string
}`;

export function validateTheme(value) {
  const errors = [];
  if (!value || typeof value !== "object") return { ok: false, errors: ["root must be an object"] };
  ensureString(value, "title", errors);
  ensureString(value, "season", errors);
  ensureString(value, "showcaseName", errors);
  ensureString(value, "showcaseDescription", errors);
  if (!Array.isArray(value.perWorkshop)) errors.push("perWorkshop must be an array");
  else {
    value.perWorkshop.forEach((ws, i) => {
      ensureString(ws, "name", errors, `perWorkshop[${i}].name`);
      ensureString(ws, "description", errors, `perWorkshop[${i}].description`);
      if (!Array.isArray(ws.modules)) errors.push(`perWorkshop[${i}].modules must be an array`);
      else {
        ws.modules.forEach((m, j) => {
          ensureString(m, "name", errors, `perWorkshop[${i}].modules[${j}].name`);
          ensureString(m, "subTheme", errors, `perWorkshop[${i}].modules[${j}].subTheme`);
        });
      }
    });
  }
  return errors.length === 0 ? { ok: true, value } : { ok: false, errors };
}

// ─── Participants ──────────────────────────────────────────────────
// One LLM call generates the whole roster; we then register them through the API.
export const participantsSchemaDescription = `{
  "participants": [
    {
      "first_name": string,
      "last_name": string,
      "username": string,                // lowercase, no spaces
      "persona_hint": string             // short tag we use to vary their responses
    }
  ]
}`;

export function validateParticipants(value, expectedCount) {
  const errors = [];
  if (!value || !Array.isArray(value.participants)) {
    errors.push("participants must be an array");
    return { ok: false, errors };
  }
  if (typeof expectedCount === "number" && value.participants.length !== expectedCount) {
    errors.push(`expected ${expectedCount} participants, got ${value.participants.length}`);
  }
  value.participants.forEach((p, i) => {
    ensureString(p, "first_name", errors, `participants[${i}].first_name`);
    ensureString(p, "last_name", errors, `participants[${i}].last_name`);
    ensureString(p, "username", errors, `participants[${i}].username`);
    ensureString(p, "persona_hint", errors, `participants[${i}].persona_hint`);
  });
  return errors.length === 0 ? { ok: true, value } : { ok: false, errors };
}

// ─── Prompt content per template ───────────────────────────────────
// The /prompts endpoint accepts { promptDataList: [{ prompt_template_id, formData }] }.
// formData shape varies by template_id. We only generate the three free-response-style
// templates plus a couple of structured ones the orchestrator may sprinkle in for
// variety. AI analysis itself only fires on 4, 6, 8 (see ai_analysis_test_cases.md).

// template_id 4 — Short Response
export function validateFormDataShortResponse(value) {
  const errors = [];
  if (!value || typeof value !== "object") return { ok: false, errors: ["formData must be an object"] };
  ensureString(value, "question", errors);
  return errors.length === 0 ? { ok: true, value } : { ok: false, errors };
}

// template_id 6 — Drag and Drop (spectrum / zones / free)
export function validateFormDataDragAndDrop(value) {
  const errors = [];
  if (!value || typeof value !== "object") return { ok: false, errors: ["formData must be an object"] };
  if (!["spectrum", "zones", "free"].includes(value.layout)) {
    errors.push("layout must be one of: spectrum | zones | free");
  }
  if (!Array.isArray(value.items) || value.items.length < 2) {
    errors.push("items must be an array with at least 2 entries");
  } else {
    value.items.forEach((it, i) => ensureString(it, "label", errors, `items[${i}].label`));
  }
  if (value.layout === "spectrum") {
    if (!value.axis || typeof value.axis !== "object") errors.push("spectrum requires axis object");
    else {
      ensureString(value.axis, "labelMin", errors, "axis.labelMin");
      ensureString(value.axis, "labelMax", errors, "axis.labelMax");
    }
  }
  if (value.layout === "zones") {
    if (!Array.isArray(value.zones) || value.zones.length < 2) errors.push("zones layout requires at least 2 zones");
    else value.zones.forEach((z, i) => ensureString(z, "label", errors, `zones[${i}].label`));
  }
  return errors.length === 0 ? { ok: true, value } : { ok: false, errors };
}

// template_id 8 — Notation
export function validateFormDataNotation(value) {
  const errors = [];
  if (!value || typeof value !== "object") return { ok: false, errors: ["formData must be an object"] };
  ensureString(value, "referenceText", errors);
  return errors.length === 0 ? { ok: true, value } : { ok: false, errors };
}

// template_id 1 — Multiple Choice (sprinkled in for variety; not analyzed)
export function validateFormDataMultipleChoice(value) {
  const errors = [];
  if (!value || typeof value !== "object") return { ok: false, errors: ["formData must be an object"] };
  ensureString(value, "question", errors);
  if (!Array.isArray(value.options) || value.options.length < 2) {
    errors.push("options must be an array of at least 2 strings");
  } else {
    value.options.forEach((opt, i) => {
      if (typeof opt !== "string" || !opt.trim()) errors.push(`options[${i}] must be a non-empty string`);
    });
  }
  return errors.length === 0 ? { ok: true, value } : { ok: false, errors };
}

// template_id 9 — Dropdown (sprinkled in for variety; not analyzed)
export function validateFormDataDropdown(value) {
  return validateFormDataMultipleChoice(value); // same shape
}

export const formDataValidatorByTemplate = {
  1: validateFormDataMultipleChoice,
  4: validateFormDataShortResponse,
  6: validateFormDataDragAndDrop,
  8: validateFormDataNotation,
  9: validateFormDataDropdown,
};

export function describeFormDataShape(templateId) {
  switch (templateId) {
    case 1:
    case 9:
      return `{ "question": string, "options": [string, string, ...] }`;
    case 4:
      return `{ "question": string }`;
    case 6:
      return `{
        "layout": "spectrum" | "zones" | "free",
        "items": [{ "label": string }, ...],
        "axis"?: { "labelMin": string, "labelMax": string },     // spectrum only
        "zones"?: [{ "label": string }, ...]                      // zones only
      }`;
    case 8:
      return `{ "referenceText": string }`;
    default:
      return "{}";
  }
}

// ─── Participant response payloads ─────────────────────────────────
// `workshop_response_content` is JSON. Shape depends on the template the response is for.
export function buildResponseShapeHint(templateId, formData) {
  switch (templateId) {
    case 1: // Multiple Choice — single index
      return `{ "selectedIndex": <integer 0..${(formData.options || []).length - 1}> }`;
    case 4: // Short Response — free text
      return `{ "text": string }`;
    case 6: // Drag and Drop — placements per item
      return `[
        {
          "keyName": <one of: ${(formData.items || []).map((i) => `"${i.label}"`).join(", ")}>,
          "position": { "x": number 0..1, "y": number 0..1 },
          "semantics": { /* optional template-specific fields */ }
        }, ...
      ]`;
    case 8: // Notation — annotation strings
      return `{ "annotations": [string, ...] }`;
    case 9: // Dropdown — single value
      return `{ "selected": <one of options> }`;
    default:
      return `{}`;
  }
}

// ─── Helpers ───────────────────────────────────────────────────────
function ensureString(obj, key, errors, label) {
  const tag = label || key;
  const v = obj?.[key];
  if (typeof v !== "string" || !v.trim()) errors.push(`${tag} must be a non-empty string`);
}
