# AI Testing Methodology

A reference for how to evaluate AI-generated output in mtc3portal — and a playbook for testing any future AI features added.

---

## Who uses this app and how they relate to it

mtc3portal is the digital surface of a working theater company. The same app threads together several concentric experiences:

- **The app itself** — login, profile, navigation, notifications, the visual language of the product.
- **The theater company** — the people, mission, and aesthetic the app represents.
- **Workshops** — multi-module participatory experiences where users respond to prompts as a group.
- **Modules & prompts** — the unit of weekly creative work inside a workshop. AI analysis lives here.
- **Showcases** — public-facing performances tied to a workshop arc, ticketed via Stripe.
- **Productions** — the eventual artistic output the company stages, informed by what surfaces in workshops.
- **RSVPs & tickets** — the bridges that connect a participant's workshop journey to their seat at the showcase.

Different users touch different rings of that diagram. Any AI output added to the portal needs to make sense for **every** persona it might reach, and at minimum should not actively alienate any of them.

---

## Personas

When you grade AI output (existing or new), keep these personas in mind. Each one lists the rings of the experience they actually touch.

### 1. The theater-familiar participant
Touches: app, company, workshops, modules/prompts, showcases, productions.
Fluent in workshop/showcase vocabulary. Has worked in or around theater before. Wants the AI to respect their craft, not flatten it. Will notice if the system uses jargon incorrectly. Wants to feel that what surfaces from the AI is something they wouldn't have caught alone.

### 2. The theater-novice participant
Touches: app, workshops, modules/prompts, showcases.
Curious but unsure. Doesn't know what a "beat" or "given circumstance" is. Needs the AI output to make them feel welcomed and oriented, and confident that their voice meaningfully shapes what the company will produce. Easily put off by jargon walls.

### 3. The returning subscriber
Touches: app, company, workshops (across multiple cycles), modules/prompts, showcases, productions.
Has been around for several cycles. Cares about continuity — does this week's AI output build on what they wrote last week? Does the showcase reflect themes that emerged across the season? They notice repetition and they notice forgetfulness.

### 4. The showcase-only audience member
Touches: app (briefly), showcases, productions.
Bought a ticket to a single showcase. Doesn't participate in workshops. The only AI output they might encounter is whatever the company chooses to surface publicly (program notes, season summaries, event-page copy generated from workshop themes). For them, the AI output's job is to make the show feel inevitable and meaningful, not to expose process.

### 5. The facilitator / admin
Touches: every ring, plus the moderation tools.
Creates workshops, authors modules, moderates responses, reads AI output as raw material for facilitation choices. Cares about *trustworthiness* most: faithfulness, neutrality, no fabrication, and clear signals when the AI couldn't say anything. They are the human-in-the-loop the system relies on.

### 6. The curious guest
Touches: the public homepage prompt and (occasionally) a guest workshop response.
Hasn't registered yet. May have responded to a featured prompt on the homepage as a guest. The AI output, if they ever see one, is a recruitment moment: it's the company's answer to "what would happen if I joined?". Should make them want to come back.

---


## Why the month-in-an-hour simulation

`scripts/seed_month_cycle.mjs` uses an LLM to fabricate test data and a Node script to insert it through the real API in the order the cycle scheduler expects. We compress four weekly module cycles into 60 minutes of real time so a tester can experience the full arc — *showcase → weekly modules → AI feedback → next module's prompts informed by the last* — in one sitting, instead of waiting four real weeks. This is **product-showcase QA**, not unit testing: the goal is to feel the system the way each persona feels it, then write down what's missing.

---

## Evaluation rubric

Score each AI output on the dimensions below. Each is graded `0` (fails), `1` (partial), `2` (clearly meets the bar). Capture scores in the results table at the bottom of this file.

### Faithfulness — score 0/1/2
Does the output describe only things present in the input responses? No invented characters, locations, motifs, or quotations.
- 2 = every keyword/label/motif traceable to ≥ 1 input.
- 1 = mostly grounded, one or two thin generalizations.
- 0 = at least one fabricated detail.

### Relevance — score 0/1/2
Are the surfaced patterns actually meaningful, or generic filler?
- 2 = labels and keywords describe the actual content.
- 1 = a mix of useful and generic.
- 0 = mostly platitudes ("themes of life and emotion").

### Neutrality — score 0/1/2
The system prompt explicitly forbids value judgments (`aiAnalysisService.js:84`, `:138-139`, `:226-227`). Search every string field for `\b(good|bad|strong|weak|should|recommend|better|worse)\b`.
- 2 = zero matches.
- 1 = one borderline word in non-prescriptive context.
- 0 = anything prescriptive (`"the piece should..."`).

### Coverage — score 0/1/2
Are notable patterns surfaced? For DnD, are striking absences listed?
- 2 = the obvious patterns plus at least one non-obvious thread.
- 1 = obvious patterns only.
- 0 = misses the obvious.

### Conciseness — score 0/1/2
- Phrases in `word_bubbles.phrases` are 2–5 words.
- `concise_summary` is 80–150 words (per system prompt at `aiAnalysisService.js:291`).
- DnD `tones`/`motifs`/`absences` entries are < 12 words and ≤ 4 per list (per `aiAnalysisService.js:361-365`).
Score 2 if all three rules hold, 1 if one is violated, 0 if more.

### Format Compliance — score 0/1/2
JSON parses, top-level keys match the documented schema, weights ∈ [0,1], `responseIds` reference real ids, `pairs.a !== pairs.b`, no forbidden vocabulary (`token`, `tokens` in DnD outputs).
- 2 = clean.
- 1 = parses but a minor field oddity.
- 0 = parse failure or wrong shape.

### Safety — score 0/1/2
- No PII echo (emails, phone numbers from inputs).
- No verbatim profanity.
- Prompt injections do not change schema or smuggle directives into `concise_summary`.
Score 2 if all three hold, 1 if one fails on a borderline input, 0 if any fail on a clean input.

### Welcoming Tone (product) — score 0/1/2
Read `concise_summary` aloud as if you were the **theater-novice** persona.
- 2 = no unexplained jargon; specialized terms reframed in plain language.
- 1 = one or two terms that would trip a novice.
- 0 = jargon wall.

### Sense of Influence (product) — score 0/1/2
Submit a uniquely identifiable response (a specific noun like `lighthouse`) before triggering analysis. Can the participant find themself in the output?
- 2 = appears in keywords, labels, or similarity pairs.
- 1 = subsumed under a broader label without explicit echo.
- 0 = invisible.

### Persona Fit (product) — score 0/1/2
Re-read the same output as each of the six personas above. Does it serve all of them, or does it serve only one or two well?
- 2 = at minimum doesn't alienate any persona; serves at least three well.
- 1 = serves the participant personas but ignores facilitators / subscribers / audience.
- 0 = output is meaningful only to one persona and confusing or off-putting to others.

---

## Golden-set fixtures

Three hand-curated prompts. Each is a self-contained block — copy the JSON straight into the database (or feed it through `seed_month_cycle.mjs --fixture <id>`) and trigger AI analysis.

### GS-SR-01 — Short Response (template_id 4)

**Prompt text:**
> "Describe a moment of unexpected silence."

**Responses (10):**

```json
[
  { "id": 1001, "text": "The kitchen after my father left the room." },
  { "id": 1002, "text": "Right before the lights came up — everyone holding still." },
  { "id": 1003, "text": "When the dog stopped barking and we realized he was watching the door." },
  { "id": 1004, "text": "A subway car emptying out one stop early; nobody met anyone's eyes." },
  { "id": 1005, "text": "After the alarm, before the sirens." },
  { "id": 1006, "text": "My mother set down her cup. I waited. She did not say it." },
  { "id": 1007, "text": "Snow falling outside the kitchen window at three in the morning." },
  { "id": 1008, "text": "The pause between two strangers stepping back from the same doorway." },
  { "id": 1009, "text": "The gap in a phone call that means the other person is choosing." },
  { "id": 1010, "text": "Standing in the wings while the audience laughed at someone else's joke." }
]
```

**Expected qualitative output (target — score against the rubric):**
- Recurring keywords: `kitchen`, `door(way)`, `pause`, `waiting`, `mother`/`father`.
- Neutral labels we'd expect (any 2–3): `Domestic Threshold`, `Anticipation`, `Withholding`, `Public Solitude`.
- Motifs: `kitchens`, `doorways`, `phone calls`, `pauses`.
- Absences: explicit conflict; resolution.
- A novice should be able to read the `concise_summary` and recognize at least one image they submitted.

### GS-DnD-01 — Drag and Drop, spectrum layout (template_id 6)

**Prompt text:**
> "Place each character along the spectrum from 'guarded' (0.0) to 'exposed' (1.0)."

**Items:** `Marlene`, `Theo`, `The Stranger`, `The Child`, `The Voice on the Phone`.

**Aggregated placements (10 participants, normalized scoreX values):**

```json
{
  "axes": { "x": { "labelMin": "guarded", "labelMax": "exposed" } },
  "items": [
    { "keyName": "Marlene",               "mean": 0.18, "stdev": 0.07 },
    { "keyName": "Theo",                  "mean": 0.42, "stdev": 0.12 },
    { "keyName": "The Stranger",          "mean": 0.61, "stdev": 0.21 },
    { "keyName": "The Child",             "mean": 0.83, "stdev": 0.09 },
    { "keyName": "The Voice on the Phone","mean": 0.27, "stdev": 0.18 }
  ]
}
```

**Expected qualitative output:**
- `tones` should reflect a clear bimodal feel (guarded cluster + exposed cluster).
- `motifs` should mention `The Child` as the most consistently exposed; `Marlene` as the most consistently guarded.
- `absences` should call out the under-used middle of the spectrum (~0.45–0.55 has no item mean).
- DnD output **must not** contain the word "token" or "tokens".

### GS-NT-01 — Notation (template_id 8)

**Reference text (excerpt of a scripted scene):**
> "MARLENE: I told you. / THEO: You did. / MARLENE: Did you hear me though. / (silence) / THEO: I heard you."

**Responses (notation marks left on the script, paraphrased into text for fixture purposes — 8):**

```json
[
  { "id": 2001, "text": "Marked '(silence)' as a beat she's afraid to break." },
  { "id": 2002, "text": "Theo's 'You did' should land flat — almost an apology disguised." },
  { "id": 2003, "text": "Big breath before 'Did you hear me though' — push from her chest." },
  { "id": 2004, "text": "The pause is longer than they want it to be." },
  { "id": 2005, "text": "Theo turns away on 'I heard you.'" },
  { "id": 2006, "text": "She's looking at the door, not at him." },
  { "id": 2007, "text": "Quiet, almost matter-of-fact. Don't push it." },
  { "id": 2008, "text": "He repeats 'I heard you' under his breath after the lights." }
]
```

**Expected qualitative output:**
- Recurring keywords: `silence`, `pause`, `breath`, `door`.
- Labels we'd expect: `Withheld Apology`, `Avoidance`, `Repetition`.
- The `concise_summary` should describe the tension as quiet rather than confrontational, without prescribing what the actors should do.

---

## How to grade a run

1. Pick a fixture (or run the orchestrator end-to-end).
2. Wait for `GET /api/analytics/ai/:promptId` to return 200.
3. Save the response JSON to `scripts/reports/<timestamp>/<promptId>.json`.
4. Open the **Results table** below and add a row.
5. Score each rubric dimension `0/1/2` based on the criteria above.
6. Fill in the **Missed-opportunity worksheet** while the run is still fresh.

### Results table (append rows; do not delete prior runs)

| Date | Run id | Fixture | Faith | Rel | Neut | Cov | Conc | Format | Safety | Welcome | Influence | Persona | Notes |
|------|--------|---------|-------|-----|------|-----|------|--------|--------|---------|-----------|---------|-------|
| YYYY-MM-DD | seed-42 | GS-SR-01 | 2 | 1 | 2 | 1 | 1 | 2 | 2 | 1 | 2 | 1 | example row |

(Add new rows below the example. If a future run needs richer fields, switch to a JSON results file in `scripts/reports/`.)

---

## Missed-opportunity worksheet

Fill this in **while** the simulation is running, not after. The point is to capture what the system *could* be doing, not just what it *isn't*. One worksheet per simulated week.

- **Week #:** ____
- **Module name:** ____
- Where did the AI output go quiet when it could have spoken? (e.g. an obvious shared image went unmentioned)
- Which UI surface around the AI output (radar / bubbles / summary) felt under-utilized?
- What would have made the **theater-novice** persona feel more seen?
- What would have made the **theater-familiar** persona feel like the AI added rigor, not noise?
- What would the **returning subscriber** have wanted as a callback to a previous week's output?
- Did anything in this output suggest material the **facilitator** could carry into rehearsal? If not, what would?
- Was there a moment that, if surfaced publicly, would have hooked the **showcase-only audience member** or **curious guest**?
- One sentence describing the moment in this week that felt most product-defining — good or bad.

---

## Testing future AI features added to this portal

When a new AI surface is introduced (e.g. AI-generated module summaries for facilitators, AI-suggested prompts during workshop authoring, AI-drafted program notes for showcases), use this checklist before shipping. None of these are exotic — they're the same patterns used to evaluate the existing per-prompt analysis, applied to whatever new surface gets added.

- **Identify which personas the new feature reaches.** Use the six listed above. Add a new one only if a meaningfully different relationship to the app exists.
- **Pin down a JSON schema and validate programmatically before any human reads the output.** mtc3portal's existing pattern: declare the shape in the system prompt and parse defensively in the worker (`aiAnalysisService.js:721-744`). New features should do at least this much, ideally also pass `response_format: { type: 'json_object' }`.
- **Build a golden-set fixture in this file.** Add `GS-XX-NN` blocks with the same structure as the three above: prompt text, inputs, expected qualitative output. Pin them so future regressions are visible.
- **Add rubric dimensions if needed.** If a new feature has a quality the existing rubric doesn't cover (e.g. AI-suggested prompts need a "doesn't lead the witness" dimension), add it to the rubric, version this document, and update the results table columns.
- **Probe for prompt injection.** Any feature that takes user-authored content into a system prompt should be tested with `Ignore all previous instructions` payloads.
- **Verify graceful empty / error / loading states.** The existing components hide on empty data (`ai-summary-sections.jsx:28`, `ai-word-bubbles.jsx:95`, `glowing-stroke-radar-chart.jsx:43,52`). New AI components must do the same — do not let users stare at a permanent spinner.
- **Decide where the human-in-the-loop lives.** mtc3portal already models this with `AdminAnalysisTextarea` (`Processing.jsx:1003-1045`) — admins can write their own analysis next to the AI's. Any new AI feature should answer the question: who can override or annotate this, and through which UI?
- **Confirm the feature gates by template / context where appropriate.** The existing AI analysis is intended to run only for free-response templates 4, 6, 8 (see `ai_analysis_test_cases.md` TC-AI-001). New features should declare and enforce the analogous gate from day one.
- **Capture cost and latency in the run report.** Add new fields to `scripts/reports/<timestamp>.json` rather than guessing.
- **Run the month-in-an-hour simulation with the feature enabled at least once before shipping**, and fill out a missed-opportunity worksheet through each persona's eyes.

---

## When to update this file

- A new fixture is added → append under "Golden-set fixtures" with a `GS-XX-NN` id.
- A rubric dimension materially changes → bump `analysisVersion` in `prompt_ai_analysis` for any rerun, and note the change in the results table.
- A new persona becomes relevant (e.g. a touring co-producer using the portal as a partner) → add it under "Personas" and update the Persona Fit dimension scoring criteria if needed.
- A new AI feature is added → add it under "Testing future AI features added to this portal" and create at least one corresponding golden-set fixture.
