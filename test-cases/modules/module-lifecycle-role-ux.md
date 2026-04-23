# Module Lifecycle & Role-Based UX — Test Cases

Supplemental Round 2 test cases covering hover / click / icon behavior across roles, progress-bar + endpoint consistency, the full BullMQ-driven lifecycle with `quick_test`, auto-repeat scheduling for `normal`, and mid-session transition consistency.

See the parent plan at [`../../docs/test-plans/modules-lifecycle-ux-test-plan.md`](../../docs/test-plans/modules-lifecycle-ux-test-plan.md).

---

### TC-MOD-033: Standard user hover/cursor affordance differs by module status

- **Feature / Requirement:** `WorkshopModules.jsx:456–579` (per-status rendering) + `App.css` (`.openButton:hover`, `.completeButton:hover`, `.adminPendingButton:hover`, no rules for `.pendingButton` or `.processingButton`) + `LockedTooltip` (`components/ui/locked-tooltip.jsx`)
- **Priority:** P1
- **Preconditions:** Standard user (not admin, no RSVP for this workshop). Workshop has one module in each of `pending`, `open`, `processing`, `completed` statuses. User has not completed all open modules (detail card should be in `locked` state).
- **Test Data:** N/A
- **Steps:**
  1. Log in as standard user and navigate to the workshop's modules page.
  2. Hover over the pending module card.
  3. Hover over the open module card.
  4. Hover over the processing module card.
  5. Hover over the completed module card.
  6. Hover over the workshop detail card (black, locked).
- **Expected Result:**
  - Pending: no background/color change on hover, no pointer cursor (bare `<button>`, no `:hover` CSS).
  - Open: card flips to black background + white text on hover, cursor is `pointer`, arrow SVG turns white (`.openButton:hover`).
  - Processing: no hover animation, no pointer cursor — lock icon visible; the card is a bare `<button>` with no `:hover` rules.
  - Completed: card flips to black + white on hover, cursor `pointer`, arrow SVG turns white (`.completeButton:hover`).
  - Detail card (locked): `LockedTooltip` bubble appears with message "Respond to all prompts in every module to unlock your RSVP." Cursor on the disabled lock button remains `default`.
- **Suggested Automation?** Partial (Playwright can assert cursor style and tooltip text; hover animation is best judged by eye)
- **Notes / Risk Covered:** Hover gating is CSS-only. A regression in `App.css` could quietly leave pending/processing cards with visual feedback that implies they are clickable — that would mislead the user.

---

### TC-MOD-034: Admin hover/cursor affordance across statuses

- **Feature / Requirement:** `WorkshopModules.jsx:497–579` (admin branches) + `Buttons.jsx:32–94` (pencil icon for admin) + `App.css` (`.adminPendingButton:hover`)
- **Priority:** P1
- **Preconditions:** Admin user. Same workshop with one module per status.
- **Test Data:** N/A
- **Steps:**
  1. Log in as admin, navigate to modules page.
  2. Hover over the pending module (should now be `.adminPendingButton`).
  3. Hover over the processing module (admin path — wrapped in `<Link>` with pencil icon).
  4. Verify the pending card's link target is `/workshops/:id/modules/:mid/prompts/edit`.
  5. Verify the processing card's link target is `/workshops/:id/modules/:mid/prompts/:first_prompt_id`.
- **Expected Result:**
  - Pending card: hover flips background to black + white text (`.adminPendingButton:hover`), cursor is `pointer`, pencil SVG is visible and white on hover.
  - Processing card: pencil icon visible; card wrapped in `<Link>`, cursor `pointer` on hover. Because RSVPStatus is not required for admin, the class may still be `processingButton` (no hover rule) — observe whether the admin gets visible hover feedback. If none, flag as a UX gap.
- **Suggested Automation?** Partial (Playwright can assert link target and icon; hover animation is manual)
- **Notes / Risk Covered:** Admin is expected to have clear editing affordance on pending and processing modules. The `processingButton` className for an admin without RSVP is an edge case worth documenting.

---

### TC-MOD-035: Processing-module click + icon gating by role and RSVP

- **Feature / Requirement:** `WorkshopModules.jsx:486–524` (`isAdmin || RSVPStatus` branch) + `Buttons.jsx:32–65` (icon switch: pencil / eye / lock)
- **Priority:** P0
- **Preconditions:** One module in `processing` status. Three user accounts: admin, RSVP user (confirmed RSVP for this workshop), standard user with no RSVP.
- **Test Data:** N/A
- **Steps:**
  1. Log in as admin. Inspect the processing module card (DOM + icon).
  2. Log in as RSVP user. Inspect the processing module card.
  3. Log in as standard user. Inspect the processing module card.
  4. In each case, click the card and observe navigation behavior.
- **Expected Result:**
  - Admin: card is wrapped in an `<a>` / `<Link>` pointing to `/prompts/:first_prompt_id`; pencil icon shown. Click navigates.
  - RSVP user: card is wrapped in a `<Link>` to the same URL; eye icon shown; className switches to `.openButton` (inherits the open hover animation). Click navigates.
  - Standard user: card is a bare `<button>` (no `<a>` ancestor); lock icon shown; click is a no-op. No navigation.
- **Suggested Automation?** Yes (Playwright per role; assert `a[href*="/prompts/"]` presence and icon `<svg>` class)
- **Notes / Risk Covered:** This is the primary authz gate for in-progress module content (AI analysis view). A regression that mis-renders a `<Link>` for a standard user would leak access to analysis content. Also validates the visual cue matches the underlying gate.

---

### TC-MOD-036: Open-module progress bar syncs after partial submission and refresh

- **Feature / Requirement:** `GET /api/workshops/:id/modulesprogress` (`workshops.js:57–90`) + `WorkshopModules.jsx:462–478` (`OpenButton` progress bar values)
- **Priority:** P0
- **Preconditions:** Standard user with one open module containing 4 prompts, 0 responses so far.
- **Test Data:** N/A
- **Steps:**
  1. Navigate to the modules page. Note the progress bar value (should be `0 / 4`).
  2. Click into the module, submit a response to one prompt, return to modules page.
  3. Observe the progress bar value.
  4. Hard refresh the modules page (Cmd+Shift+R).
  5. Observe the progress bar value again.
- **Expected Result:**
  - After step 2, the bar reflects `1 / 4` without a manual reload (the effect re-runs on route change via `location.pathname` in the dependency array).
  - After step 4 (hard refresh), the bar still reads `1 / 4` — values come from the API, not client cache.
  - Network tab shows a fresh `GET /modulesprogress` returning `response_count: 1` for this module.
- **Suggested Automation?** Yes (Playwright can fill + submit + reload and assert `<progress value="1" max="4">`)
- **Notes / Risk Covered:** Progress is tightly coupled to backend state. If the dependency array on the effect changes or the endpoint SQL shifts, this sync can silently break.

---

### TC-MOD-037: `/modulesprogress` only returns modules in `open` status

- **Feature / Requirement:** `workshops.js:57–90` — both inner queries filter `wm.workshop_module_status = "open"`
- **Priority:** P0
- **Preconditions:** Authenticated user. Workshop with at least one module in each of `open`, `processing`, `completed`, `pending`.
- **Test Data:** Bearer token for any authenticated user
- **Steps:**
  1. Call `GET /api/workshops/:workshopid/modulesprogress` with the bearer token.
  2. Inspect the returned array.
- **Expected Result:**
  - 200 OK with an array.
  - Each element has `{ module_id, prompt_count, response_count }`.
  - Only `open`-status modules are present — no `pending`, `processing`, or `completed` modules appear.
  - Number of elements equals the number of open modules in the workshop.
- **Suggested Automation?** Yes (pytest + requests — drop into `automation/api/modules/`)
- **Notes / Risk Covered:** Regression guard. If the SQL filter is accidentally relaxed, the modules page would render progress bars on processing/completed cards that should be read-only.

---

### TC-MOD-038: Full `quick_test` cycle end-to-end — status grouping, cycle_jobs, notifications

- **Feature / Requirement:** `cycleScheduler.js:103–222` (start) + `moduleWorker.js:22–151` (status + side-effects) + `WorkshopModules.jsx:276–549` (status grouping render)
- **Priority:** P0
- **Preconditions:** Admin user. Workshop has 1 pending module with ≥1 prompt and no existing cycle. `moduleWorker` running. Cycle config saved with preset = `quick_test`.
- **Test Data:** N/A
- **Steps:**
  1. (Admin) POST `/api/cycle/start/:workshopId`. Note the returned `schedule.openAt / processingAt / completedAt`.
  2. Open the modules page in a second tab as a standard user (should currently show the module under Pending).
  3. Wait for the `openModule` job to fire (immediate for `quick_test`).
  4. Refresh the modules page — module should now appear under Open.
  5. Wait ~2 minutes for `processModule` to fire.
  6. Refresh — module should move to Processing.
  7. Wait another ~2 minutes for `completeModule` to fire.
  8. Refresh — module should appear under Completed.
  9. During each step inspect `cycle_jobs` rows via MySQL and `pm2 logs moduleWorker` output.
- **Expected Result:**
  - After step 1: three `cycle_jobs` rows inserted with `status = 'pending'` and timestamps matching the schedule.
  - After each transition: the corresponding `cycle_jobs` row flips to `status = 'completed'` (`moduleWorker.js:66–75`).
  - Worker logs `Worker received job: openModule`, `processModule`, `completeModule` at the expected times.
  - `moduleOpen` notification is enqueued on the open transition (`moduleWorker.js:56–63`).
  - `analyzePrompt` jobs are enqueued on the processing transition (one per prompt).
  - UI sections render/hide correctly based on which modules remain in each status.
- **Suggested Automation?** Partial (status transitions are trivial to assert; timing is long and benefits from manual observation)
- **Notes / Risk Covered:** Highest-value end-to-end confidence test for the lifecycle. Exercises UI rendering, worker, DB, and queue interactions together.

---

### TC-MOD-039: `lastDayReminder` notification fires ~12s before `processModule`

- **Feature / Requirement:** `cycleScheduler.js:180` — `reminderDelay = Math.max(0, procDelay - 12000)`
- **Priority:** P2
- **Preconditions:** Same as TC-MOD-038. `quick_test` preset.
- **Test Data:** N/A
- **Steps:**
  1. Start the cycle (`POST /api/cycle/start/:workshopId`).
  2. Note the `processingAt` timestamp from the response.
  3. Tail notification worker logs (`pm2 logs notificationWorker` or equivalent).
  4. Record the timestamp at which `lastDayReminder` processes and the timestamp at which `processModule` fires.
- **Expected Result:**
  - `lastDayReminder` fires ≈ 12 seconds before the `processModule` job.
  - For `quick_test` (2-minute delay), that means at ~108 seconds after `openModule`.
  - Delta between `lastDayReminder` and `processModule` is `12000 ms ± worker startup jitter`.
- **Suggested Automation?** Partial (comparing logged timestamps can be scripted; end-to-end observation is manual)
- **Notes / Risk Covered:** Value is hard-coded and likely a development placeholder. Captured in open questions — this test simply confirms the current observable behavior until product clarifies intent.

---

### TC-MOD-040: Auto-repeat only schedules the next cycle when `auto_repeat = TRUE`

- **Feature / Requirement:** `moduleWorker.js:101–148` (calls `scheduleNextCycle` on final completed) + `cycleService.js:47–77` (guards on `auto_repeat = TRUE`, pending modules, and all prompts present)
- **Priority:** P1
- **Preconditions:** Admin user. Workshop with 2 modules (both in `pending` with prompts).
- **Test Data:** Two runs — one with preset `quick_test` (`auto_repeat = FALSE`) and one with preset `normal` (`auto_repeat = TRUE`). Use a workshop where `start_day`/`start_hour` resolve to the next weekday so the scheduled `openAt` is observable.
- **Steps:**
  1. **Run A (quick_test)**: Save config with `quick_test`. Start cycle. Wait until all modules complete. Verify whether new `cycle_jobs` rows appear.
  2. **Run B (normal)**: Re-create the pending modules. Save config with `normal`. Manually push the status to `completed` for every module (simulate end-of-cycle) via `PUT /modules/:id` to avoid waiting 72+ hours. Verify new `cycle_jobs` rows appear.
- **Expected Result:**
  - Run A: after the final `completeModule` fires, worker logs `All modules completed for workshop …, checking auto-repeat...`. `scheduleNextCycle` is called but returns early because `auto_repeat = FALSE` — NO new `cycle_jobs` rows are inserted.
  - Run B: `scheduleNextCycle` inserts three new `cycle_jobs` rows per pending module and enqueues BullMQ jobs with delays matching the next weekly occurrence. `materialsReady` notification is enqueued for eligible users.
  - Warning log appears if auto-repeat is silently skipped because one pending module lacks prompts (create a pending module without prompts to verify this branch in a third sub-run, if time allows).
- **Suggested Automation?** No (observation-based; timing and DB state)
- **Notes / Risk Covered:** Silent failure risk. Auto-repeat skipping doesn't notify the admin — worth documenting.

---

### TC-MOD-041: Workshop detail card state transitions `locked → rsvp-ready → confirmed`

- **Feature / Requirement:** `WorkshopModules.jsx:249–266` (`allOpenModulesCompleted`, `detailCardState`, `detailCardColors`) + `LockedTooltip` (`components/ui/locked-tooltip.jsx`)
- **Priority:** P1
- **Preconditions:** Standard user. Workshop with 2 open modules, each having 2 prompts. User has 0 responses. No RSVP row exists.
- **Test Data:** N/A
- **Steps:**
  1. Navigate to modules page. Hover the detail card.
  2. Submit responses for all prompts in module 1 only. Return to modules page. Hover the detail card again.
  3. Submit responses for all prompts in module 2. Return to modules page (or observe post-submit flow). Hover the detail card.
  4. Confirm the RSVP (via `PUT` to `/workshops/:id/rsvp/:userId/confirm` or whatever the confirm flow is). Refresh the modules page. Hover the detail card.
- **Expected Result:**
  - Step 1: `detailCardState = 'locked'`. Card background is black, RSVP button disabled with lock icon, tooltip appears on hover with message "Respond to all prompts in every module to unlock your RSVP."
  - Step 2: Still `locked` (not all open modules complete). Tooltip still shows.
  - Step 3: `detailCardState = 'rsvp-ready'`. Card background is `#D2A478` (gold/brown), button reads "RSVP" and navigates on click. No tooltip.
  - Step 4: `detailCardState = 'confirmed'`. Card background is `#57A15E` (green), button reads "View RSVP". No tooltip.
  - CSS transition is visible during each state change (`transition: background-color 0.4s ease` inline on the card).
- **Suggested Automation?** Partial (Playwright can assert background color and button text; tooltip appearance is best judged manually)
- **Notes / Risk Covered:** The three-color state machine is a high-signal UX cue. A regression in the memo dependencies would strand users in locked state or over-unlock them.

---

### TC-MOD-042: Mid-session lifecycle transition consistency — open module becomes processing while user is interacting

- **Feature / Requirement:** `moduleWorker.js:36–51` (processing update) + `workshops.js:57–90` (progress endpoint filters by `status = open`) + `WorkshopModules.jsx:150–205` (modules effect re-runs on route change, not polling)
- **Priority:** P2
- **Preconditions:** Standard user. Workshop has 1 module in `open` with 3 prompts. User has answered 1 prompt. Admin has `quick_test` cycle running and `processModule` will fire in the next ~30 seconds.
- **Test Data:** N/A
- **Steps:**
  1. On the user's modules page, verify the module appears under Open with progress `1 / 3`.
  2. Without reloading, observe the card while the worker transitions the module to `processing` (time it with `pm2 logs moduleWorker`).
  3. After `Worker received job: processModule` is logged, click into the module card (should still be under Open on the stale page render).
  4. Return to the modules page (this triggers the effect to re-fetch, because `location.pathname` changes on navigation).
  5. Observe how the card is rendered now.
  6. Hard refresh the modules page and observe again.
- **Expected Result:**
  - Step 1: module shown under Open, progress `1 / 3`.
  - Step 2: no automatic update — card remains as-rendered until the page effect re-runs.
  - Step 3: navigation into the module still works (the link was captured while the user's client still believed the module was open). The prompts page may show stale state; document what actually happens.
  - Steps 4–5: module is now rendered under Processing. The user's `response_count` for this module is NO LONGER present in `/modulesprogress` (the endpoint filters to `open` only), so the progress bar disappears. This is expected but is a visibility gap — the user has no way from this page to see that their previously-submitted response is still in the DB.
  - Step 6: same as step 5 — state is backed by the API, not the client.
- **Suggested Automation?** No (requires coordinated timing across two sessions)
- **Notes / Risk Covered:** Consistency-across-refresh scenario. Documents the user-visible side effect of `/modulesprogress` filtering to `open` status — the user's submitted work "disappears" from the progress UI as soon as the module transitions, even though it's preserved in the DB. Useful evidence for a future UX improvement (e.g. show a frozen "submitted" indicator on processing modules for users who responded).

---
