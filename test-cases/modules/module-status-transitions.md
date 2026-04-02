### TC-MOD-007: Admin manually changes module status via API

- **Feature / Requirement:** `PUT /api/workshops/:workshopid/modules/:moduleid` (`workshops.js:768–779`)
- **Priority:** P0
- **Preconditions:** Admin token. Module exists in `pending` status.
- **Test Data:** `{ newStatus: "open" }`
- **Steps:**
  1. Call `PUT /api/workshops/1/modules/5` with `{ newStatus: "open" }`.
- **Expected Result:** 201 response. Module status updated in DB. Next GET shows `workshop_module_status = "open"`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Backend does NOT validate `newStatus` against an enum. Arbitrary strings (e.g. `"banana"`) would be accepted.

- **Actual Result:** 201 response. Module status updated in DB. Next GET shows `workshop_module_status = "open"`.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-MOD-008: Cycle scheduler starts and queues all three transitions

- **Feature / Requirement:** `POST /api/cycle/start/:workshopId` (`cycleScheduler.js:103–200`)
- **Priority:** P0
- **Preconditions:** Admin token. Cycle config saved. At least one pending module with prompts.
- **Test Data:** Workshop with 2 pending modules, each having ≥1 prompt. Preset: `quick_test`.
- **Steps:**
  1. Save cycle config with `quick_test` preset.
  2. Call `POST /api/cycle/start/:workshopId`.
- **Expected Result:**
  - 3 BullMQ jobs enqueued per module: `openModule`, `processModule`, `completeModule`.
  - `cycle_jobs` table populated with all jobs.
  - With `quick_test`, open fires immediately, processing ~2min later, completed ~4min later.
- **Suggested Automation?** Partial (can verify job creation; timing needs observation)
- **Notes / Risk Covered:** Happy path for the automated lifecycle.

---

### TC-MOD-009: Cycle start rejects workshop with no pending modules

- **Feature / Requirement:** `cycleScheduler.js:122–124`
- **Priority:** P1
- **Preconditions:** All modules in the workshop are already `open` or `completed`.
- **Test Data:** Workshop where all modules have status other than `pending`.
- **Steps:**
  1. Call `POST /api/cycle/start/:workshopId`.
- **Expected Result:** 400 `{ error: "No pending modules found for this workshop." }`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Negative path — prevents re-cycling already-active modules.

---

### TC-MOD-010: Cycle start rejects modules without prompts

- **Feature / Requirement:** `cycleScheduler.js:127–146` — validation that every pending module has ≥1 prompt
- **Priority:** P0
- **Preconditions:** Admin has created a module but has not added prompts to it.
- **Test Data:** Pending module with 0 prompts.
- **Steps:**
  1. Save cycle config. Call `POST /api/cycle/start/:workshopId`.
- **Expected Result:** 400 `{ error: "Some modules are missing prompts", modules: [...] }` listing the offending modules.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Critical guard — opening an empty module would give users nothing to respond to.

- **Actual Result:** 400 `{ error: "Some modules are missing prompts", modules: [...] }` listing the offending modules.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-MOD-011: Worker transitions module from pending → open

- **Feature / Requirement:** `moduleWorker.js:32–33` — `openModule` job sets status to `open`
- **Priority:** P0
- **Preconditions:** Module exists in `pending` status. `openModule` job queued.
- **Test Data:** N/A (worker-driven).
- **Steps:**
  1. Observe module status after `openModule` job fires.
- **Expected Result:**
  - DB: `workshop_module_status = 'open'`.
  - `moduleOpen` notification is enqueued (`moduleWorker.js:56–63`).
  - Corresponding `cycle_jobs` row marked `completed`.
- **Suggested Automation?** Yes (integration test with quick_test preset)
- **Notes / Risk Covered:** Happy path for automated open.

---

### TC-MOD-012: Worker transitions module from open → processing

- **Feature / Requirement:** `moduleWorker.js:36–37` + lines 78–99
- **Priority:** P0
- **Preconditions:** Module in `open` status.
- **Test Data:** N/A.
- **Steps:**
  1. Observe after `processModule` job fires.
- **Expected Result:**
  - DB: `workshop_module_status = 'processing'`.
  - AI analysis jobs enqueued for each prompt in the module.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** The processing transition also triggers downstream AI work.

---

### TC-MOD-013: Worker transitions module from processing → completed

- **Feature / Requirement:** `moduleWorker.js:40–41` + lines 101–148
- **Priority:** P0
- **Preconditions:** Module in `processing` status.
- **Test Data:** N/A.
- **Steps:**
  1. Observe after `completeModule` job fires.
- **Expected Result:**
  - DB: `workshop_module_status = 'completed'`.
  - If ALL modules in the workshop are now completed, `scheduleNextCycle` is called and `materialsReady` notification enqueued.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** End of module lifecycle + auto-repeat trigger.

---

### TC-MOD-014: Worker handles unknown job name gracefully

- **Feature / Requirement:** `moduleWorker.js:44–46` — `default` case logs `Unknown job`
- **Priority:** P2
- **Preconditions:** N/A.
- **Test Data:** Job with name `"unknownJob"` queued to `moduleQueue`.
- **Expected Result:** Worker logs "Unknown job: unknownJob". The subsequent `db.execute` will attempt `SET workshop_module_status = undefined` — this will likely throw a DB error. **Risk: no early return before the UPDATE.**
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Bug: `newStatus` is undefined in the default case but the worker still executes the UPDATE query.

---
