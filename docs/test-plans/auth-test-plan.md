# Authentication Test Plan

## Related Artifacts
- Test Cases: [`test-cases/auth/`](../../test-cases/auth/)
- Execution Reports:
  - [`auth-execution-round-1.md`](../../test-execution/auth-execution-round-1.md)
  - [`auth-execution-round-2.md`](../../test-execution/auth-execution-round-2.md)
- Bug Reports: [`bug-reports/`](../../bug-reports/)
- Observability Improvements: [`observability-improvements.md`](../../artifacts/observability-improvements.md)
- Templates: [`test-case-template.md`](../../templates/test-case-template.md)

---

## 1. Test Plan ID
TP-AUTH-001

## 2. Overview
This test plan covers authentication and authorization functionality for the application, including login, registration, logout, password reset, email confirmation, session handling, and JWT-based access control.

The goal of this plan is to verify that users can securely access the application according to their role and account state, and that the system handles authentication failures, invalid sessions, and recovery flows correctly.

Initial execution (Round 1) identified areas where backend behavior could not be fully verified due to limited observability. Targeted instrumentation was introduced to improve verification of authentication flows, enabling stronger validation in subsequent execution (Round 2).

---

## 3. Objectives
- Verify users can register, log in, and log out successfully
- Verify authentication failures are handled correctly
- Validate password reset and email confirmation flows
- Verify JWT-based session handling and protected route enforcement
- Confirm role-based authorization works as expected
- Identify security, validation, and UX risks related to authentication
- Ensure sufficient observability exists to verify backend authentication behavior without exposing sensitive data

---

## 4. Scope

### In Scope
- User login with valid and invalid credentials
- Registration and post-registration login behavior
- Logout behavior
- Forgot password flow
- Reset password flow
- Email confirmation and resend confirmation flow
- JWT validation on protected routes
- Admin vs non-admin authorization behavior
- Auth-related frontend validation and error messaging
- Auth-related UI state, such as logged-in vs logged-out display behavior

### Out of Scope
- Third-party SSO or OAuth integrations
- Performance/load testing of login endpoints
- Penetration testing beyond basic auth and authorization checks
- Full email delivery infrastructure validation outside functional flow checks
- Browser compatibility testing beyond selected primary browser(s)

---

## 5. Test Items
The following items are covered by this plan:
- Authentication UI forms
- Authentication API endpoints
- JWT middleware and protected route handling
- Registration flow
- Password recovery flow
- Email verification flow
- Role-based access behavior
- Session-related UI state

---

## 6. Test Approach

### Manual Testing
Manual testing will be used to verify:
- End-to-end user flows
- Validation messages
- Error handling
- Redirect behavior
- UI state changes
- Exploratory auth edge cases

### Automated Testing
Automation will be used for:
- High-value regression flows
- Repeatable login and logout scenarios
- Protected route access checks
- Password reset and registration happy paths where practical
- API-level authorization validation

### Risk-Based Prioritization
Testing priority will focus first on:
1. Core login and logout functionality
2. Protected route enforcement
3. Password reset and account recovery
4. Role-based access restrictions
5. Registration and email confirmation
6. UX polish and non-critical edge cases

### Execution Strategy

Testing is performed in two phases:

**Round 1 — Baseline Execution**
- Test cases executed under initial system conditions
- Verification based on:
  - API responses
  - UI behavior
  - client-side state (e.g., localStorage)
- Observability gaps documented where backend behavior could not be directly confirmed

**Round 2 — Targeted Re-Execution**
- Focused re-testing of selected auth cases impacted by:
  - missing or unclear backend logging
  - async side effects (e.g., queue jobs)
  - token issuance and validation paths
- Verification enhanced using:
  - server-side instrumentation logs
  - improved traceability of auth decisions
- Goal: upgrade previously inconclusive or partially verified results to fully validated outcomes

---

## 7. Test Types
- Functional Testing
- Negative Testing
- Validation Testing
- Boundary Testing
- Session / Authorization Testing
- Basic Security Testing
- Regression Testing
- UI / UX Testing

---

## 8. Entry Criteria
Testing will begin when:
- The application is running in a usable local, QA, or staging environment
- Relevant auth endpoints are available
- Required test users and test data exist
- Core auth flows are implemented
- Tester has access to logs, browser dev tools, and API inspection tools as needed

---

## 9. Exit Criteria
Testing for this phase is complete when:
- All planned critical and high-priority auth test cases have been executed
- Round 1 results are documented with any limitations clearly noted
- Targeted Round 2 re-execution has been completed for affected test cases
- Previously inconclusive or partially verified results have been re-evaluated where applicable
- Critical defects have been documented
- Observability gaps have been identified and addressed where necessary
- Major authentication risks have been identified and summarized

---

## 10. Test Environment
- Environment: Local development
- Frontend: React (Vite) on `localhost:5173`
- Backend: Node.js / Express on `localhost:3036`
- Database: MySQL
- Queue: Redis + BullMQ
- Authentication Method: JWT
- Primary Browser: Chrome
- Supporting Tools: Browser DevTools, curl, PM2 logs, Playwright (Python), Python `requests`, screenshots

---

## 11. Test Data
The following test data is required:
- Valid standard user account
- Valid admin account
- Valid guest or alternate-role account if applicable
- Non-existent user account data
- Invalid password combinations
- Expired and tampered token samples
- Valid and invalid password reset tokens
- Valid and invalid email confirmation tokens

Example categories:
- Valid email and password
- Invalid password
- Empty inputs
- Whitespace-padded inputs
- Expired JWT
- Invalid JWT
- Deleted-user token case
- Unverified email account

---

## 12. Roles and Responsibilities

| Role | Responsibility |
|------|----------------|
| QA Engineer | Design test cases, execute tests, document issues, summarize risks |
| Developer | Clarify intended behavior, investigate issues, implement fixes |
| Product Owner / Reviewer | Confirm expected behavior and business rules where needed |

---

## 13. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Invalid or expired JWT handling may produce confusing UX | Users may appear logged in but fail on API actions | Execute session and protected-route tests, document redirect/error behavior |
| Missing frontend route guards | Users may access partial UI while unauthorized | Verify protected pages manually and document gaps |
| No refresh-token flow | Sessions may fail abruptly after token expiry | Include expired-token scenarios and note UX impact |
| User enumeration through auth-related messaging | Security risk | Verify login and forgot-password messages remain generic |
| Missing rate limiting on login | Brute-force risk | Document as security concern even if not directly fixed in this phase |
| Token payload includes unnecessary user data | Potential information exposure | Review token contents and note risk in findings |
| Role changes may be inconsistent between UI and backend | Incorrect admin UI display or access assumptions | Test admin/non-admin scenarios and stale token behavior |
| Limited backend observability for auth flows | Incomplete verification of system behavior | Introduce targeted logging and perform Round 2 re-validation |

---

## 14. Deliverables
- Authentication test plan
- Authentication test cases
- Authentication execution report (Round 1)
- Authentication execution report (Round 2)
- Bug reports related to auth flows
- Observability improvement documentation
- Screenshots, logs, and supporting evidence
- Automation coverage for selected auth scenarios

---

## 15. Traceability

| Feature Area | Test Cases | Execution | Bugs |
|-------------|-----------|----------|------|
| Login | test-cases/auth/login.md | auth-execution-round-1.md, auth-execution-round-2.md | bug-reports/... |
| Registration | test-cases/auth/registration.md | auth-execution-round-1.md, auth-execution-round-2.md | bug-reports/... |
| Password Reset | test-cases/auth/forgot-password.md | auth-execution-round-1.md, auth-execution-round-2.md | bug-reports/... |
| JWT / Session | test-cases/auth/session-jwt.md | auth-execution-round-1.md, auth-execution-round-2.md | bug-reports/... |
| Role Authorization | test-cases/auth/session-jwt.md | auth-execution-round-1.md, auth-execution-round-2.md | bug-reports/... |

---

## 16. Assumptions
- JWT authentication is the primary access control mechanism
- Test users can be created or seeded as needed
- Email-related flows can be functionally validated even if external delivery is mocked or partially simulated
- Local storage or equivalent client storage is used for session persistence
- Admin-only routes and standard protected routes are available for validation

---

## 17. Constraints
- Testing may be limited by incomplete environments or seeded data
- Full email delivery confirmation may depend on infrastructure outside the application
- Some negative security scenarios may be validated through observation rather than full exploit testing
- Time constraints may require prioritizing critical auth flows over lower-risk UI polish cases

---

## 18. Approval
| Name | Role |
|------|------|
| Corey Brewer | QA Engineer |

## 19. Execution Summary

### Round 1 Summary
- Core authentication functionality validated across login, registration, and protected routes
- Several test cases produced expected outcomes but lacked direct backend verification
- Observability gaps identified in:
  - token validation paths
  - queue-based notification flows
  - response payload verification

### Round 2 Focus
- Targeted re-execution of authentication scenarios impacted by observability limitations
- Verification enhanced using server-side instrumentation
- Emphasis on:
  - confirming rejection reasons (invalid, expired, malformed tokens)
  - validating async job behavior (password reset notifications)
  - verifying token issuance during reset flows

### Outcome
- Improved confidence in authentication behavior
- Reduced reliance on inferred client-side outcomes
- Stronger alignment between expected behavior and verifiable system execution
