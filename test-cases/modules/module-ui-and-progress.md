### TC-MOD-015: Modules are grouped by status on the modules page

- **Feature / Requirement:** `WorkshopModules.jsx:276–279` — filters by `open`, `processing`, `completed`, `pending`
- **Priority:** P0
- **Preconditions:** Workshop has modules in multiple statuses.
- **Test Data:** 1 open, 1 processing, 1 completed, 1 pending module.
- **Steps:**
  1. Navigate to the workshop's modules page.
- **Expected Result:**
  - Open modules show under "Open" heading with progress bar.
  - Processing modules show under "Processing" heading.
  - Completed modules show under "Completed" heading.
  - Pending modules show under "Pending" heading.
  - Section headings only render if that status has modules.
- **Suggested Automation?** Yes (Playwright)
- **Notes / Risk Covered:** Core display logic.

- **Actual Result:** When workshop has multiple modules in multiple status states, the workshop modules page is organized by those different statuses. When there is no module in a certain status, the section doesn’t show up on the page.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-MOD-016: Open modules show per-module progress (responses / prompts)

- **Feature / Requirement:** `GET /api/workshops/:workshopid/modulesprogress` (`workshops.js:57–90`); displayed via `OpenButton` in `WorkshopModules.jsx:462–478`
- **Priority:** P0
- **Preconditions:** Open module with 5 prompts. User has responded to 3.
- **Test Data:** N/A.
- **Steps:**
  1. Navigate to workshop modules page.
- **Expected Result:** The open module card shows progress: `3 / 5` (or the equivalent visual bar). The values come from the API's `prompt_count` and `response_count`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** The modulesprogress query only counts modules with `workshop_module_status = "open"`. Progress for processing/completed modules is NOT returned. This is because modules in processing and completed statuses are no longer accepting responses, processing is for admin and users who completed the module review and completed is when the module becomes an archive that features previous responses and analysis.

- **Actual Result:** The open module card shows progress: `3 / 5` (or the equivalent visual bar). The values come from the API's `prompt_count` and `response_count`.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-MOD-017: Pending modules link to editor for admins, no link for regular users

- **Feature / Requirement:** `WorkshopModules.jsx:552–579`
- **Priority:** P1
- **Preconditions:** Pending module exists.
- **Test Data:** N/A.
- **Steps:**
  1. (Admin) Navigate to modules page → pending module is a clickable link to `/prompts/edit`.
  2. (Regular user) Navigate to modules page → pending module is rendered as a non-clickable card.
- **Expected Result:** Admin gets a Link, regular user gets a static button.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Role-based UI behavior.

---

### TC-MOD-018: Processing modules are accessible only to admins and RSVP holders

- **Feature / Requirement:** `WorkshopModules.jsx:497–520`
- **Priority:** P1
- **Preconditions:** Module in processing status. Regular user without RSVP.
- **Test Data:** N/A.
- **Steps:**
  1. (Admin) → processing module is clickable link.
  2. (User with RSVP) → processing module is clickable link.
  3. (User without RSVP) → processing module is a non-clickable card.
- **Expected Result:** Link rendering depends on `isAdmin || RSVPStatus`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Gating visibility of processing-phase content.

---

## TC-MOD-019: Progress bar shows in header during open-phase module reading

- **Feature / Requirement:** `Root.jsx:24,27` — `isOpenPhaseReader && !isEditor` → `showProgressBar = true`
- **Priority:** P0
- **Preconditions:** User navigates to a prompt within an open module.
- **Test Data:** Open module, route `/workshops/1/modules/2/prompts/3`.
- **Steps:**
  1. Navigate to prompt within an open module (passing `moduleStatus: 'open'` via router state).
- **Expected Result:** Progress bar is visible in the header. Shows `current / max` values.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Progress bar only shows for `open` status — hidden for `processing` and `completed`.

---

### TC-MOD-020: Progress count updates after fetching from API

- **Feature / Requirement:** `WorkshopPromptsPage.jsx:159–178` — `GET /api/workshops/modules/:moduleid/progress`
- **Priority:** P0
- **Preconditions:** User is in a module with 4 prompts, has responded to 2.
- **Test Data:** N/A.
- **Steps:**
  1. Navigate into the module.
- **Expected Result:** Progress context is set to `{ current: 2, max: 4 }`. Progress bar reflects this.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** `max` is set from `promptsList.length` on the frontend (not the API). `current` comes from `GET /modules/:moduleid/progress` → `count`.

---

### TC-MOD-021: Module complete flag set when current === max

- **Feature / Requirement:** `WorkshopPromptsPage.jsx:180–184` — `setModuleComplete(progressState.current === promptsList.length)`
- **Priority:** P1
- **Preconditions:** User has responded to all prompts in the module.
- **Test Data:** Module with 3 prompts, 3 responses.
- **Steps:**
  1. Navigate into the module.
- **Expected Result:** `moduleComplete` state is `true`.
- **Suggested Automation?** Yes (verify via DOM state or behavior)
- **Notes / Risk Covered:** This drives end-of-module behavior when the last prompt is submitted.

---

### TC-MOD-029: Workshop Detail card shows locked state when user has not completed all open modules

- **Feature / Requirement:** `WorkshopModules.jsx:249–266` — `detailCardState` derivation
- **Priority:** P1
- **Preconditions:** User has NOT completed all open modules. No RSVP for workshop exists.
- **Test Data:** Workshop with 4 open modules, user completed 1.
- **Steps:**
  1. Navigate to workshop modules page.
- **Expected Result:** Workshop detail card background is black (`#000000`). RSVP button shows a lock icon, is disabled. Tool tip appears when hovering.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Visual gating of RSVP access.

- **Actual Result:** When user completed only one of multiple modules, the workshop detail card is in black and the RSVP button shows a lock icon. When hovering over, a tool tip pops up explaining why.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-MOD-030: Detail card transitions to rsvp-ready when all open modules completed

- **Feature / Requirement:** `allOpenModulesCompleted` memo at `WorkshopModules.jsx:249–257`
- **Priority:** P1
- **Preconditions:** User has completed all open modules (response_count ≥ prompt_count for each). RSVP may or may not exist yet.
- **Test Data:** N/A.
- **Steps:**
  1. Navigate to modules page after completing all open modules.
- **Expected Result:** Card shows gold/brown background (`#D2A478`). "RSVP" button is active, navigates to RSVP page.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Transitional UI state.

---

### TC-MOD-031: Detail card shows confirmed state when RSVP is confirmed

- **Feature / Requirement:** `detailCardState === 'confirmed'` at `WorkshopModules.jsx:262`
- **Priority:** P1
- **Preconditions:** RSVP exists with `rsvp_confirmation_status = 'confirmed'`.
- **Test Data:** N/A.
- **Steps:**
  1. Navigate to modules page.
- **Expected Result:** Card shows green background (`#57A15E`). Button reads "View RSVP".
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Final confirmed state.

---

### TC-MOD-032: Admin submits prompts via editor

- **Feature / Requirement:** `POST /api/workshops/:workshopid/modules/:moduleid/prompts` (`workshops.js:689–749`); triggered from `WorkshopsPromptsEditor.jsx:56–74`
- **Priority:** P0
- **Preconditions:** Admin on the prompt editor page for a pending module.
- **Test Data:** 2 prompts: one Multiple Choice (template 1), one Short Response (template 4).
- **Steps:**
  1. Select "Multiple Choice" from dropdown, configure options, click Next.
  2. Select "Short Response", configure question, click Submit (header button).
- **Expected Result:**
  - API returns 201 `"Prompts Inserted Successfully"`.
  - Prompts are inserted in `workshop_prompts` table.
  - Success message "Prompts added and module is now open!" shown on screen.
  - **Note:** Module status does NOT change to open — the editor comment says "Module stays pending — the cycle scheduler controls status transitions."
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Contrary to the success message text, the module remains `pending`. Status only changes when the cycle scheduler fires or admin manually updates.

- **Actual Result:** When an admin configures a short response and multiple choice prompt and clicks submit, a message appears: “Prompts added and module is now open”. API returns 201 with success message. DB table workshop_prompts gets two new rows inserted.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---
