# QA Portfolio — Full-Stack Application Testing

ISTQB-certified QA Engineer with hands-on experience testing a real full-stack web application across authentication, module lifecycle, and async notification systems.

Full web app code repo available upon request.

---

## Start Here

If you only review one part of this portfolio, start with:

1. **Auth Test Execution (Round 1 → Round 2)**
   - [`test-execution/auth-execution-round-1.md`](test-execution/auth-execution-round-1.md)
   - [`test-execution/auth-execution-round-2.md`](test-execution/auth-execution-round-2.md)  
   Shows full QA workflow: baseline testing → identified observability gaps → backend instrumentation → re-validation with stronger evidence

2. **Observability Improvements**
   - [`artifacts/observability-improvements.md`](artifacts/observability-improvements.md)  
   Backend instrumentation added to improve testability and verification confidence

3. **Authentication Test Plan**
   - [`docs/test-plans/auth-test-plan.md`](docs/test-plans/auth-test-plan.md)  
   Scope, risk analysis, entry/exit criteria, and execution strategy

4. **Test Cases**
   - [`test-cases/auth/`](test-cases/auth/)  
   Structured test design with expected results, actual results, and evidence references

### What to Look For

- Identification of inconclusive test results due to missing backend observability
- Targeted instrumentation to resolve verification gaps
- Progression from baseline execution to fully verified outcomes
- Evidence-backed validation using UI, API, server logs, and database checks
- Security findings including an IDOR vulnerability and missing input validation

---

## Application Under Test

The system under test is a full-stack web application built with:

| Layer | Technology |
|-------|------------|
| Frontend | React (Vite) |
| Backend | Node.js + Express |
| Database | MySQL |
| Queue System | Redis + BullMQ |
| Payments | Stripe |
| Notifications | Postmark (email), Twilio (SMS) |

The application is a modular platform where members and administrators collaboratively shape in-person theater workshops and productions. Key features include JWT-based authentication, a time-based module lifecycle (Pending → Open → Processing → Completed), interactive prompt templates, admin moderation and analytics, RSVP and QR-based event check-in, and an async notification system powered by BullMQ workers.

---

## QA Scope

Testing focused on validating critical user flows and identifying defects across three feature areas:

- **Authentication** — Login, registration, logout, password reset, email confirmation, JWT session handling, role-based authorization
- **Modules** — Lifecycle state transitions, response submission, progress tracking, RSVP completion logic, admin permissions
- **Notifications** — Transactional and preference-gated delivery, settings API validation, authorization enforcement, worker behavior

---

## Testing Approach

Testing followed a structured, phased approach:

### Test Planning & Design
Defined scope, risk areas, and entry/exit criteria for each feature. Designed test cases covering positive flows, negative flows, and edge cases. Prioritized using risk-based analysis.

### Execution — Round 1 (Baseline)
- Validated end-to-end flows using API responses, UI behavior, and client-side state
- Core functionality confirmed across all three feature areas
- Identified **observability gaps** where backend behavior could not be directly verified

### Observability Improvements
- Introduced targeted backend instrumentation for token validation, queue job tracking, and auth flow traceability
- Documented in [`artifacts/observability-improvements.md`](artifacts/observability-improvements.md)

### Execution — Round 2 (Targeted Re-Validation)
- Re-tested previously inconclusive cases using server-side logs and improved traceability
- Upgraded all targeted cases to fully verified outcomes

### Bug Reporting
Documented defects with reproducible steps, expected vs. actual results, severity/priority classification, root cause analysis, and supporting evidence.

### Automation
Implemented automation using:
- **Python + `requests`** — API test scripts for auth, modules, and notification endpoints
- **Playwright (Python)** — UI test specs for authentication flows, module interactions, and notification settings

---

## Portfolio Structure

```
qa_portfolio_mtc/
├── docs/                    # Test strategy, environment setup, traceability matrix
│   └── test-plans/          # Per-feature test plans (auth, modules, notifications)
├── test-cases/              # Structured test cases by feature
│   ├── auth/
│   ├── modules/
│   └── notifications/
├── test-execution/          # Execution reports with metrics and findings
├── bug-reports/             # Defect documentation by severity
├── artifacts/               # Observability improvements, AI usage documentation
├── automation/              # API and UI automation scripts (Python)
│   ├── api/                 # requests + pytest
│   └── playwright/          # Playwright + pytest
├── test-data/               # Test fixtures (users, modules, notifications, prompts)
├── templates/               # Reusable templates for test artifacts
└── reports/                 # Screenshots and execution evidence
```

---

## Key Findings

- **IDOR vulnerability** — Authenticated users could modify other users' notification settings via API ([bug report](bug-reports/major.md))
- **Missing input validation** — Module status endpoint accepted arbitrary values, risking data integrity ([bug report](bug-reports/major.md))
- **Auth state not invalidated** — Expired JWT sessions left the UI in an authenticated state ([bug report](bug-reports/critical.md))
- **Notification flood** — Simultaneous module opens produced redundant per-module emails instead of aggregated notifications ([bug report](bug-reports/minor.md))
- **Observability gaps** — Round 1 testing identified areas where API responses alone were insufficient to verify backend behavior, leading to targeted instrumentation improvements

---

## What This Demonstrates

- **Test process ownership** — End-to-end QA workflow from planning through execution, defect reporting, and re-validation
- **Observability-driven testing** — Identifying verification gaps and improving system testability rather than accepting inconclusive results
- **Security awareness** — Finding authorization vulnerabilities (IDOR) and input validation gaps through systematic testing
- **Full-stack understanding** — Testing across frontend, backend API, database, async job queues, and third-party integrations
- **Structured documentation** — Test plans, traceability matrices, and execution reports aligned with industry standards
- **Automation capability** — API and UI test automation using Python, `requests`, and Playwright
- **Effective AI usage** — Leveraging AI for acceleration while maintaining ownership of execution, judgment, and findings ([details](artifacts/ai-usage.md))
