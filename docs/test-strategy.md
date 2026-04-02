# Test Strategy

## Purpose

This document defines the overall testing strategy applied across all feature areas in this QA effort. It describes the testing levels, techniques, prioritization approach, tooling, and decision criteria used throughout the project.

Individual test plans for each feature area are maintained separately in `test-plans/`.

---

## Scope

The strategy covers three feature areas of the application:

- **Authentication** — Login, registration, logout, password reset, email confirmation, JWT session handling, role-based authorization
- **Modules** — Module lifecycle management, response submission, progress tracking, RSVP completion, admin permissions
- **Notifications** — Transactional and preference-gated delivery, settings API, authorization, worker behavior

---

## Test Levels

### Manual Functional Testing
Primary method for validating end-to-end user flows, edge cases, and exploratory scenarios. Used across all feature areas.

### API Testing
Direct endpoint validation using curl and Python `requests`. Used to verify backend behavior independently of frontend logic, including authorization enforcement, input validation, and response structure.

### UI Testing
Browser-based validation of frontend behavior, form validation, redirect logic, and state management. Performed manually and supplemented with Playwright automation.

### Automation
- **API automation** — Python + `requests` for repeatable endpoint validation (auth, modules, notifications)
- **UI automation** — Playwright (Python) for high-value regression flows (login, registration, logout, settings)

---

## Test Techniques

- **Equivalence partitioning** — Grouping inputs into valid/invalid classes (e.g., valid credentials vs. wrong password vs. non-existent user)
- **Boundary value analysis** — Testing at input limits (e.g., password length constraints, empty fields)
- **Negative testing** — Verifying correct rejection of invalid inputs, unauthorized access, and malformed data
- **State transition testing** — Validating module lifecycle behavior (Pending → Open → Processing → Completed)
- **Risk-based prioritization** — Focusing execution on high-impact, high-likelihood failure areas first
- **Exploratory testing** — Supplementing structured test cases with unscripted investigation of system behavior

---

## Prioritization Approach

Test execution is prioritized using a risk-based approach:

1. **Critical path flows** — Login, registration, protected route access, module submission
2. **Security boundaries** — Authorization enforcement, token validation, IDOR prevention
3. **State-dependent behavior** — Module lifecycle transitions, RSVP completion logic, progress tracking
4. **Async system behavior** — Queue job processing, notification delivery, worker error handling
5. **Validation and UX** — Input validation, error messaging, UI state consistency

This ordering is reflected in both test plan scoping and execution round selection.

---

## Execution Strategy

Testing is performed in iterative rounds:

### Round 1 — Baseline
- Execute high-priority test cases across all feature areas
- Document results with evidence (screenshots, API responses, log excerpts)
- Identify observability gaps where backend behavior cannot be fully verified

### Observability Improvements
- Introduce targeted backend instrumentation to address verification gaps
- Focus on token validation logging, queue job traceability, and auth decision paths

### Round 2 — Targeted Re-Validation
- Re-execute previously inconclusive or partially verified test cases
- Use enhanced server-side logging to achieve fully verified outcomes

Subsequent rounds may extend to lower-priority test cases, deeper edge case coverage, or additional feature areas.

---

## Defect Management

Defects are documented with:
- Reproducible steps
- Expected vs. actual results
- Severity and priority classification
- Root cause analysis
- Evidence (screenshots, logs, API responses)

Bug reports are organized by severity in `bug-reports/` (critical, major, minor).

---

## Test Environment

- **Environment:** Local development
- **Frontend:** React (Vite) on `localhost:5173`
- **Backend:** Node.js / Express on `localhost:3036`
- **Database:** MySQL
- **Queue:** Redis + BullMQ
- **Browser:** Chrome (primary), Safari (secondary)
- **Tools:** Browser DevTools, curl, PM2 logs, Playwright, Python `requests`

Full environment setup instructions are in [`environment-setup.md`](environment-setup.md).

---

## Entry and Exit Criteria

### Entry Criteria (per round)
- Application is running and reachable
- Test accounts are available (admin and regular user)
- Required test data exists
- Tester has access to logs, DevTools, and API inspection tools

### Exit Criteria (per round)
- All planned test cases for the round have been executed
- Results are documented with evidence
- Defects are reported with severity classification
- Observability gaps (if any) are identified and documented
- Execution summary is completed

---

## Risks

- Testing is performed in a local development environment; behavior may differ in staging or production
- Some async behaviors (queue timing, email delivery) introduce non-determinism
- Application is under active development; features may change between test rounds
- Limited observability in Round 1 required instrumentation improvements before full verification was possible

---

## Traceability

Test coverage is tracked in [`traceability-matrix.md`](traceability-matrix.md), which maps feature requirements to test cases, execution reports, known bugs, and automation coverage across all three feature areas.
