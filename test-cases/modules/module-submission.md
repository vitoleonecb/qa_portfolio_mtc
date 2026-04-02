### TC-MOD-022: Submitting a response via the new endpoint

- **Feature / Requirement:** `POST /api/workshops/:workshopid/modules/:moduleid/prompts/:promptid/response` (`workshops.js:793–826`)
- **Priority:** P0
- **Preconditions:** Authenticated user. Open module.
- **Test Data:** `{ workshop_response_content: {...}, prompt_template_id: 1 }`
- **Steps:**
  1. Respond to a prompt and click submit.
- **Expected Result:**
  - 201 `{ ok: true, prompt_id: <number> }`.
  - Row inserted in `workshop_responses`.
  - For template IDs 1, 3, 6, 7, 9: `workshop_response_acceptance = 1` (auto-accepted).
  - For template ID 4, 8: `workshop_response_acceptance = 0` (requires moderation).
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Auto-accept logic at `workshops.js:806`.

- **Actual Result:**  Server returned `201` for both submissions. One response submitted against an open-ended prompt (template ID `8`) was inserted into `workshop_responses` with `workshop_response_acceptance = 0`. One response submitted against a closed-ended prompt (template ID `1`) was inserted into `workshop_responses` with `workshop_response_acceptance = 1`. Database results matched the expected auto-accept behavior by prompt template type.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-MOD-023: Empty response is blocked on frontend

- **Feature / Requirement:** `WorkshopPromptsPage.jsx:399–411` — `isEmptyResponse(responseData)` guard
- **Priority:** P1
- **Preconditions:** User has not interacted with the prompt template.
- **Test Data:** Default empty responseData.
- **Steps:**
  1. Click submit without selecting/entering anything.
- **Expected Result:** `handleSubmit` returns `false`. No API call made. Console logs "Nothing to submit".
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Client-side guard. Backend has no equivalent empty-response validation.

---

### TC-MOD-024: After last prompt submit, handleEndOfModule determines next action

- **Feature / Requirement:** `WorkshopPromptsPage.jsx:437–497`
- **Priority:** P0
- **Preconditions:** User is on the last prompt of an open module.
- **Test Data:** Module with 3 prompts. User is on prompt 3.
- **Steps:**
  1. Submit response on the last prompt.
- **Expected Result:** `handleEndOfModule` fires:
  - Fetches `modulesprogress` for the workshop.
  - If other unfinished modules exist → sets `nextModulePath` and `remainingModules`.
  - If ALL modules complete → creates RSVP via `POST /api/workshops/rsvp/create`, sets `RSVPEarned = true`.
  - `endOfPrompts` is set to `true`, which renders `ModuleEdge`.
- **Suggested Automation?** Partial (full E2E integration)
- **Notes / Risk Covered:** This is the critical module-completion decision point.

- **Actual Result:** When user is submitting their last prompt, handleEndOfModule fires, fetches the progress in the overall workshop’s modules, if there are some unanswered prompts, then the number of modules to complete appears with a button to go to it, if all prompts are finished, then the rsvp page is returned, and rsvp is inserted in DB.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-MOD-025: ModuleEdge screen — remaining modules

- **Feature / Requirement:** `EdgePages.jsx:40–66` — `ModuleEdge` component
- **Priority:** P0
- **Preconditions:** User completed module 1, but modules 2 and 3 are unfinished.
- **Test Data:** `remainingModules = 2`.
- **Steps:**
  1. Complete the last prompt in module 1.
- **Expected Result:** Screen shows "Module Complete!" with "2 modules left to RSVP." and "Next" / "Leave" buttons. "Next" links to the first prompt of the next unfinished module.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Verifies correct remaining count and navigation path.

---

### TC-MOD-026: ModuleEdge screen — all modules complete, RSVP earned

- **Feature / Requirement:** `EdgePages.jsx:46–53` — `remainingModules === 0` branch
- **Priority:** P0
- **Preconditions:** User just completed the last prompt of the last open module.
- **Test Data:** `remainingModules = 0`, `RSVPEarned = true`.
- **Steps:**
  1. Complete the final prompt of the final module.
- **Expected Result:** Screen shows "Module Complete!" with "Your RSVP is ready." and "RSVP" / "Leave" buttons. "RSVP" navigates to `/workshops/:workshopId/rsvp/:userId`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Full completion happy path.

- **Actual Result:** When user is submitting their last prompt and all other prompts under the same workshop have been responded to: Edge page shows with text explaining they now have an RSVP available with a next button that will redirect them to their RSVP’s page.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-MOD-027: RSVP auto-created on final prompt submission (legacy endpoint)

- **Feature / Requirement:** `workshops.js:210–237` — the older POST endpoint checks view-based RSVP readiness
- **Priority:** P1
- **Preconditions:** User has responded to all prompts across all modules in the workshop. Using the legacy endpoint.
- **Test Data:** N/A.
- **Steps:**
  1. Submit the final response through the legacy `POST /:workshopid/modules/:moduleid/prompts/:promptid`.
- **Expected Result:**
  - Compares `number_of_prompts_per_workshop_view.length === user_rsvp_ready_view.length`.
  - If equal → RSVP row inserted, `workshopRsvpUnconfirmed` notification enqueued.
  - 201 with RSVP message.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** The new endpoint (`/response`) does NOT do this RSVP check — the frontend handles it in `handleEndOfModule` instead. **Risk: Two different RSVP-creation code paths exist.**

---

### TC-MOD-028: RSVP created via frontend's handleEndOfModule

- **Feature / Requirement:** `WorkshopPromptsPage.jsx:479–492`
- **Priority:** P0
- **Preconditions:** All modules complete (no unfinished in progressData).
- **Test Data:** N/A.
- **Steps:**
  1. Complete last prompt of last module (triggers handleEndOfModule).
- **Expected Result:** Frontend calls `POST /api/workshops/rsvp/create` with `{ user_id, workshop_id }`. RSVP row created. `RSVPEarned` set to true.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** This is the active code path for RSVP creation in the Vite app.

- **Actual Result:** When user is submitting their last prompt and all other prompts under the same workshop have been responded to: Frontend calls `POST /api/workshops/rsvp/create` with `{ user_id, workshop_id }`. RSVP row created. RSVPEarned set to true.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---
