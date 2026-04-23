# Modules — Lifecycle & Role-Based UX Test Plan

## Related Artifacts
- Parent Plan: [`modules-test-plan.md`](modules-test-plan.md)
- Test Cases: [`test-cases/modules/module-lifecycle-role-ux.md`](../../test-cases/modules/module-lifecycle-role-ux.md)
- Execution Reports: [`mod-execution-round1.md`](../../test-execution/mod-execution-round1.md)
- Bug Reports: [`bug-reports/`](../../bug-reports/)
- Templates: [`test-case-template.md`](../../templates/test-case-template.md)

---

## 1. Test Plan ID
TP-MOD-002

## 2. Overview

This is a **supplemental** plan that extends [`TP-MOD-001`](modules-test-plan.md) with deeper coverage of two complex areas of the modules feature:

1. **Lifecycle timing** — Module state transitions (`pending → open → processing → completed`) driven by BullMQ workers, admin cycle triggers, and the auto-repeat path for the `normal` preset.
2. **Role-based UX** — How the modules page renders clickable links, bare buttons, icons, hover affordances, and a gated detail card differently for admin users, RSVP holders, and standard users without RSVP.

The parent plan already validated admin-only creation, status-transition authorization, scheduler guardrails, and baseline UI grouping. This plan covers the downstream UX and workflow consistency concerns that surface once those basics are in place.

---

## 3. Code-Informed Feature Summary

**Lifecycle state machine.** Module status is stored in `workshop_modules.workshop_module_status` with four values (`pending`, `open`, `processing`, `completed`). Admins can transition status manually through `PUT /api/workshops/:workshopid/modules/:moduleid` (`workshops.js:768–779`) — this endpoint accepts any string for `newStatus` and has no enum validation (known bug `BUG-MOD-001`). Automated transitions are driven by BullMQ: `POST /api/cycle/start/:workshopId` (`cycleScheduler.js:103–222`) enqueues three `moduleQueue` jobs per pending module (`openModule`, `processModule`, `completeModule`) with delays derived from the saved `cycle_config` and a `lastDayReminder` on `notificationQueue` at `processDelay − 12s`. `moduleWorker.js:22–151` applies each status update, writes the matching `cycle_jobs` row to `completed`, enqueues `moduleOpen` on open, enqueues `analyzePrompt` jobs for every prompt in the module on processing, and on `completed` calls `scheduleNextCycle(workshopId)` (`services/cycleService.js:47`) plus enqueues `materialsReady` for users who responded to every module.

**Role and RSVP gating.** The frontend derives `isAdmin` from `GET /api/users/:id/isadmin` (`WorkshopModules.jsx:210–216`) and `RSVPStatus` from `GET /api/workshops/:id/rsvp/:userId/status` (`WorkshopModules.jsx:95–118`). Each lifecycle section in `WorkshopModules.jsx` renders differently:

- **Open** (456–483) — always rendered as a `<Link>` for any authenticated user, wrapping an `OpenButton` with a live progress bar bound to `response_count / prompt_count` from `GET /api/workshops/:id/modulesprogress` (`workshops.js:57–90`). That endpoint only returns rows for modules whose status is currently `open`.
- **Processing** (486–524) — wrapped in `<Link>` only when `isAdmin || RSVPStatus`; otherwise rendered as a bare `<button>` with no click target. The rendered icon is pencil (admin), eye (RSVP holder), or lock (standard). When `RSVPStatus` is truthy the CSS class flips from `.processingButton` to `.openButton`, which gives the card a black-on-white hover animation it otherwise lacks.
- **Completed** (526–549) — always rendered as a read-only `<Link>` for every user.
- **Pending** (551–579) — `<Link>` only for admin (→ `/prompts/edit`); otherwise a bare button. The button class switches from `.pendingButton` (no hover rules in `App.css`) to `.adminPendingButton` (explicit black hover) for admins.

**Detail card + tooltip.** The workshop detail card has three states (`locked`, `rsvp-ready`, `confirmed`) computed in `detailCardState` (`WorkshopModules.jsx:261–266`). `locked` renders a disabled button with a `<LockedTooltip>` (`components/ui/locked-tooltip.jsx`) whose bubble appears on mouse-enter and hides on scroll. Transitions between states happen reactively as `allOpenModulesCompleted` and `RSVPStatus` change, typically after the user completes the last prompt or the RSVP row is confirmed.

**Notifications and AI side-effects.** Each transition enqueues downstream work: `moduleOpen`, `lastDayReminder`, `analyzePrompt` jobs (one per prompt), `materialsReady`, plus the auto-repeat branch if the workshop's config has `auto_repeat = TRUE` (only the `normal` preset sets this). This is what makes the lifecycle interesting from a QA angle — the worker is not just flipping a flag, it's a coordinator for multiple downstream queues.

---

## 4. Objectives

- Verify UI hover, cursor, and icon behavior matches the user's role and the module's status
- Verify the processing-module click gate (`isAdmin || RSVPStatus`) works at the link and icon level
- Verify `GET /modulesprogress` continues to filter to `open` status only, even after a transition
- Verify progress bars re-sync correctly after partial response submission and page refresh
- Verify the automated lifecycle fires all three BullMQ jobs with correct timing (using `quick_test`)
- Verify `lastDayReminder` fires at the intended offset relative to the `processModule` job
- Verify auto-repeat only scheduling occurs for workshops whose config has `auto_repeat = TRUE`
- Verify workshop detail card state (`locked → rsvp-ready → confirmed`) transitions reactively
- Identify any gaps where state changes require a manual reload to reflect correctly

---

## 5. Scope

### In Scope
- Hover, cursor, and icon rendering for module cards across all four statuses × {admin, RSVP user, standard user}
- Clickability and link target of module cards per role and status
- Progress bar sync after response submission and refresh
- Behavior of `GET /api/workshops/:id/modulesprogress` across status transitions
- End-to-end timing with `quick_test` cycle preset
- `lastDayReminder` offset relative to processing transition
- Auto-repeat scheduling for `normal` preset
- Workshop detail card state machine and locked tooltip
- Mid-session transitions (module moves from `open` to `processing` while a user is interacting with it)

Associated test case file:
- `test-cases/modules/module-lifecycle-role-ux.md` (TC-MOD-033 through TC-MOD-042)

### Out of Scope
- Re-validation of admin-only creation/deletion (covered by TP-MOD-001)
- Manual-status-change enum validation (covered by BUG-MOD-001)
- Notification delivery internals (deferred to the notifications feature area)
- AI analysis content correctness
- Stripe / membership gating behavior
- Exhaustive concurrency testing across multiple simultaneous users

---

## 6. Assumptions

- Admin, RSVP-holding, and standard user accounts are all seeded and reachable
- A workshop exists with modules in each of the four lifecycle states for at least one scenario
- The `moduleWorker` process (`node workers/moduleWorker.js`) is running and connected to Redis
- The `quick_test` cycle preset is available for fast end-to-end lifecycle observation
- Test execution can observe DevTools network traffic and MySQL `cycle_jobs` rows
- Browser viewport is desktop-sized (the hover behaviors are mouse-only)

---

## 7. Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hover gating is CSS-only — regressions in `App.css` can quietly remove affordance cues | Standard users lose visual signal that a module is not clickable | Tests that directly inspect hover state and cursor style |
| Progress bar is driven by a status-filtered endpoint — mid-session transitions can cause the bar to vanish after refresh | Confusing UX; user may think their response wasn't saved | Mid-session transition test with explicit refresh step |
| `lastDayReminder` delay uses a hard-coded `12000 ms` offset (`cycleScheduler.js:180`) — likely a test-mode value carried into production | Users may receive reminders seconds before processing instead of hours | Explicit timing test; flagged in open questions |
| Auto-repeat is quietly skipped when any module lacks prompts (`cycleService.js:74–77`) | Workshops can stall between cycles without a visible error | Verify warning log and lack of new `cycle_jobs` rows |
| Detail-card state derives from a memoized progress comparison — race conditions between fetches could keep a user locked after completing | Gated RSVP access when it should be unlocked | Explicit check after final prompt submission |
| `OpenButton` hard-codes `"72 hrs"` label regardless of the cycle preset's `open_to_processing_hours` | Misleading user expectation on non-normal presets | Flagged in open questions; potential cosmetic bug |

---

## 8. Priority Areas

Priority for this plan is weighted toward scenarios that would produce a visible UX defect or a stalled workflow:

1. **P0** — Role-gated links on processing modules (a mis-gated `<Link>` leaks access to AI analysis to unauthorized users)
2. **P0** — Progress-endpoint status filter (regression risk every time the query changes)
3. **P0** — Full cycle timing with `quick_test` (the highest-value end-to-end confidence test)
4. **P1** — Hover / cursor / icon affordances per role (UX signal integrity)
5. **P1** — Auto-repeat scheduling for `normal` preset (silent failure risk)
6. **P1** — Detail card state transitions + tooltip
7. **P2** — `lastDayReminder` offset verification (timing correctness)
8. **P2** — Mid-session transition consistency after refresh

---

## 9. Suggested Evidence to Capture

For each executed case, capture at least two of the following:

- Screenshot of the modules page in the described state (with DevTools hover simulation where relevant)
- DevTools screenshot of the relevant API call showing request/response (`/modulesprogress`, `/cycle/start/*`, etc.)
- MySQL query result from `cycle_jobs` showing job rows and `status` column
- `pm2 logs` excerpt showing the worker log lines (`Worker received job: openModule …`, `Auto-repeat: scheduled next cycle for workshop …`, etc.)
- Recorded video or screen capture for the cycle timing cases (TC-MOD-038 and TC-MOD-039) because the evidence is temporal

---

## 10. Manual vs Automation Split

| Case | Recommended Approach | Rationale |
|------|---------------------|-----------|
| TC-MOD-033 hover/cursor matrix for standard user | Manual | CSS hover is hard to assert from automation; a human eye is the best observer |
| TC-MOD-034 hover affordance for admin | Manual | Same as above |
| TC-MOD-035 processing-module click gating | Both | Manual for UI; Playwright can verify link target and icon rendering |
| TC-MOD-036 progress bar refresh sync | Both | Playwright can drive submit + reload and assert bar value |
| TC-MOD-037 progress endpoint status filter | Automation (pytest + requests) | Pure API assertion |
| TC-MOD-038 quick_test cycle end-to-end | Manual (initial) → Automation (integration) | Timing-heavy; best to observe manually first |
| TC-MOD-039 lastDayReminder offset | Manual | Requires observing notification queue timing |
| TC-MOD-040 auto-repeat (normal preset) | Manual | Long runtime; observation-based |
| TC-MOD-041 detail card state transitions | Both | Playwright for UI state; manual for tooltip feel |
| TC-MOD-042 mid-session transition consistency | Manual | Requires coordinated timing between tabs/sessions |

---

## 11. Entry Criteria
- Parent plan TP-MOD-001 Round 1 has been executed and the tracked bugs are known
- Backend + frontend + MySQL + Redis + `moduleWorker` are running locally
- Three test accounts exist: admin, RSVP-holding user, standard (no-RSVP) user
- A dedicated workshop is available for cycle timing (can be reset between runs)

## 12. Exit Criteria
- All 10 test cases (TC-MOD-033 through TC-MOD-042) have been executed and marked
- Any newly-reproduced defects are filed in `bug-reports/`
- Ambiguities in Section 13 are either resolved or explicitly handed to the developer
- A short execution entry exists in `test-execution/` summarizing the round

---

## 13. Open Questions / Ambiguities

- `lastDayReminder` offset of 12 seconds (`cycleScheduler.js:180`, mirrored in `cycleService.js:96`) looks like a dev-mode value. Is 12 seconds the intended production behavior for `normal` preset, or should it scale with `open_to_processing_hours`?
- `OpenButton` hard-codes `"72 hrs"` text (`Buttons.jsx:103`). Should it reflect the actual `open_to_processing_hours` from the active cycle config, or is the fixed label intentional branding?
- `WorkshopModules.jsx:336–362` empty-state branch renders `<CreateButton>` without gating on `isAdmin`. A standard user with a workshop that has zero modules will see the Create button. Confirm whether this is intentional (backend rejects on submit regardless) or should be gated in the UI.
- `PUT /api/workshops/:workshopid/modules/:moduleid` still accepts arbitrary `newStatus` strings. Do we want a regression case in this plan or do we continue to rely on the existing tracked `BUG-MOD-001`?
- Does the `auto_repeat` skip path in `cycleService.js:74–77` surface anywhere visible to the admin, or is the warning log the only signal? If silent, that's a testability gap worth filing.

---

## 14. Deliverables
- This plan (`docs/test-plans/modules-lifecycle-ux-test-plan.md`)
- Test cases (`test-cases/modules/module-lifecycle-role-ux.md`)
- Execution entry to be added once Round 2 runs
- Any new bug reports surfaced in `bug-reports/`
- Supporting screenshots / logs in `reports/`

---

## 15. Approval
| Name | Role |
|------|------|
| Corey Brewer | QA Engineer |
