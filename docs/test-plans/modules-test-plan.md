# Modules Test Plan

## Related Artifacts
- Test Cases: [`test-cases/modules/`](../../test-cases/modules/)
- Execution Reports:
  - [`mod-execution-round1.md`](../../test-execution/mod-execution-round1.md)
- Bug Reports: [`bug-reports/`](../../bug-reports/)
- Templates: [`test-case-template.md`](../../templates/test-case-template.md)

---

## 1. Test Plan ID
TP-MOD-001

## 2. Overview

This test plan defines the scope, approach, and priorities for testing the modules feature.

The goal is to validate the highest-risk workflows tied to module management, status behavior, user response flow, progress tracking, and RSVP readiness. This plan supports the module test cases stored in `test-cases/modules/`.

---

## 3. Feature Overview

The modules feature allows administrators to create and manage workshop modules, control prompt authoring, and move modules through lifecycle states. It also allows users to interact with open modules by submitting prompt responses, tracking progress, and earning RSVP access after completion.

Because this feature depends on role permissions, lifecycle state, and completion logic, testing is prioritized around those dependencies.

---

## 4. Objectives
- Verify admin-only module actions are properly restricted
- Verify module lifecycle behavior works as expected (Pending → Open → Processing → Completed)
- Validate modules display correctly in the UI grouped by status
- Verify user progress is reflected accurately
- Validate prompt submission through the intended flow
- Verify end-of-module behavior routes the user correctly
- Confirm RSVP readiness behavior reflects completion state
- Verify admin prompt setup behaves as expected

---

## 5. Scope

### In Scope
- Module creation (UI and API)
- Permission enforcement (admin vs. regular user)
- Manual status transitions via API
- Scheduler validation behavior (reject modules without prompts)
- Modules page UI grouping by status
- Progress display and tracking
- Response submission
- End-of-module flow and navigation
- RSVP state on modules page
- Prompt editor submission

Associated test case files:
- `test-cases/modules/module-creation.md`
- `test-cases/modules/module-status-transitions.md`
- `test-cases/modules/module-submission.md`
- `test-cases/modules/module-ui-and-progress.md`
- `test-cases/modules/modules-overview.md`

### Out of Scope
- Full regression of every module edge case
- Deep queue timing validation for all BullMQ transitions
- Performance or load testing
- Full concurrency testing
- Every low-priority UI guard or cosmetic issue

These may be covered in a later round.

---

## 6. Test Approach

### Manual Testing
Manual testing will be used to verify:
- End-to-end module workflows
- Status transition behavior
- UI grouping and progress display
- Permission boundaries
- RSVP completion logic
- Exploratory edge cases

### Automated Testing
Automation will be used for:
- API-level authorization validation (admin vs. non-admin)
- Status transition endpoint validation
- Response submission via API
- Module creation and deletion

### Risk-Based Prioritization
Priority is given to:
1. Admin permission boundaries
2. Status transition behavior and data integrity
3. Response submission and progress tracking
4. End-of-module and RSVP completion logic
5. UI grouping and display correctness
6. Prompt editor behavior

---

## 7. Test Types
- Functional Testing
- Negative Testing
- Validation Testing
- State Transition Testing
- Authorization Testing
- UI / UX Testing

---

## 8. Round 1 Planned Coverage

The following test cases are planned for Round 1 execution:

- TC-MOD-001 — Admin creates a module via the UI
- TC-MOD-003 — Non-admin API call to create module is rejected
- TC-MOD-007 — Admin manually changes module status via API
- TC-MOD-010 — Cycle start rejects modules without prompts
- TC-MOD-015 — Modules are grouped by status on the modules page
- TC-MOD-016 — Open modules show per-module progress
- TC-MOD-022 — Submitting a response via the new endpoint
- TC-MOD-024 — After last prompt submit, handleEndOfModule determines next action
- TC-MOD-026 — ModuleEdge screen shows RSVP earned when all modules are complete
- TC-MOD-028 — RSVP created via frontend handleEndOfModule
- TC-MOD-029 — Detail card shows locked state when user has not completed all open modules
- TC-MOD-032 — Admin submits prompts via editor

---

## 9. Entry Criteria
Testing will begin when:
- Application is running locally
- Admin and regular user accounts are available
- Workshop test data is available (at least one workshop with modules)
- Prompt templates exist for module authoring and submission testing
- Required pages and routes are reachable
- Tester has access to logs, DevTools, and API inspection tools

---

## 10. Exit Criteria
This test plan is complete for Round 1 when:
- All selected Round 1 test cases have been executed
- Each test case has a recorded status with evidence
- Confirmed issues are documented as bug reports
- Execution results are summarized in the Round 1 execution file

---

## 11. Test Environment
- Environment: Local development
- Frontend: React (Vite) on `localhost:5173`
- Backend: Node.js / Express on `localhost:3036`
- Database: MySQL
- Queue: Redis + BullMQ
- Primary Browser: Chrome
- Supporting Tools: Browser DevTools, curl, PM2 logs, Playwright (Python), Python `requests`, screenshots

---

## 12. Test Data
The following test data is required:
- At least one workshop
- Modules in multiple statuses (pending, open, processing, completed)
- Prompt templates for module authoring
- Admin user account
- Regular user account with partial and full module completion states

---

## 13. Roles and Responsibilities

| Role | Responsibility |
|------|----------------|
| QA Engineer | Design test cases, execute tests, document issues, summarize risks |
| Developer | Clarify intended behavior, investigate issues, implement fixes |

---

## 14. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Invalid module statuses accepted by backend | Corrupted lifecycle state, inconsistent UI behavior | Test with invalid status values, document validation gaps |
| Prompt editor messaging does not match true module state | Admin confusion about module availability | Verify success messages reflect actual system state |
| Dual RSVP creation paths (frontend and backend) | Inconsistent RSVP behavior | Test both code paths, document differences |
| Progress and completion logic tightly coupled to module status | UI sync issues, incorrect completion state | Verify progress updates after each response submission |
| Permission boundaries critical for admin-only functionality | Unauthorized access to module management | Test non-admin access via UI and API |

---

## 15. Traceability

| Feature Area | Test Cases | Execution | Bugs |
|-------------|-----------|----------|------|
| Module Creation | test-cases/modules/module-creation.md | mod-execution-round1.md | bug-reports/... |
| Status Transitions | test-cases/modules/module-status-transitions.md | mod-execution-round1.md | bug-reports/major.md |
| Submission | test-cases/modules/module-submission.md | mod-execution-round1.md | bug-reports/... |
| UI and Progress | test-cases/modules/module-ui-and-progress.md | mod-execution-round1.md | bug-reports/... |

---

## 16. Assumptions
- Workshop and module data can be created or seeded as needed
- Module lifecycle transitions can be triggered manually via API or through the scheduler
- BullMQ and Redis are available in the test environment
- Admin and regular user accounts are available for role-based testing

---

## 17. Constraints
- Testing performed in a local development environment
- Full scheduler timing validation is out of scope for Round 1
- Concurrent user scenarios are not covered in this round
- Some module edge cases may require specific data states that are difficult to reproduce consistently

---

## 18. Approval
| Name | Role |
|------|------|
| Corey Brewer | QA Engineer |

---

## 19. Deliverables
- Module test case files in `test-cases/modules/`
- Module execution report for Round 1
- Bug reports for reproduced defects
- Supporting screenshots and evidence in `reports/`

---

## 20. Execution Summary

### Round 1 Summary
- 12 high-priority test cases executed with 100% pass rate
- Key bugs identified:
  - Module status endpoint accepts invalid values (promoted to bug report — major)
  - Prompt editor success message is misleading (promoted to bug report — minor)
  - Module progress not updated to 100% at edge page (documented as observation)
- Validation gap identified: backend does not enforce module name length restriction
- All selected lifecycle, permission, and completion behaviors validated
