# Auth Test Execution — Round 2

## Overview

Round 2 focuses on re-validating selected authentication test cases after implementing observability improvements documented in [`artifacts/observability-improvements.md`](../artifacts/observability-improvements.md).

Goal: Increase confidence by verifying internal system behavior alongside API responses.

- Total Test Cases (in scope for Round 2): 6
- Executed: 6
- Passed: 6
- Failed: 0
- Inconclusive: 0
- Blocked: 0

- Execution Rate: 100%
- Pass Rate: 100%

---

## Scope Covered
- Previously inconclusive or partially verified tests
- Critical authentication flows
- Areas impacted by improved backend logging

---

## Execution Summary

| Test ID | Title | Status | Notes |
|--------|------|--------|------|
| TC-AUTH-013 | Authenticated route rejects request with invalid/tampered token | Pass | R1: 403 observed, response body not verified → R2: rejection reason verified with improved logging / direct response evidence |
| TC-AUTH-014 | Authenticated route rejects expired token | Pass | R1: 403 observed, message body not verified and UI state remained authenticated → R2: rejection reason verified and post-401 behavior rechecked |
| TC-AUTH-019 | Forgot password — valid email sends reset link | Pass | R1: 200 observed, resetPassword enqueue not verifiable → R2: queue enqueue verified through instrumentation logs |
| TC-AUTH-020 | Forgot password — non-existent email | Pass | R1: 200 response, no queue visibility → R2: Logs confirm no enqueue action taken |
| TC-AUTH-022 | Reset password — valid token and strong password | Pass | R1: password update observed, accessToken issuance not directly verified → R2: token issuance verified through instrumentation / response evidence |
| TC-AUTH-024 | Reset password — token with wrong `type` claim rejected | Pass | R1: 400 observed, rejection reason not verified → R2: wrong-token-type rejection reason directly verified |

---

## Key Outcome
- All 6 previously inconclusive test cases upgraded to fully verified Pass
- Observability improvements confirmed effective for:
  - Token rejection reason verification (invalid, expired, wrong-type)
  - Queue enqueue confirmation for password reset flow
  - Access token issuance verification during reset
- Reduced reliance on inferred client-side outcomes

---

## Evidence
- `../reports/TC-AUTH-013-round2.png`
- `../reports/TC-AUTH-014-round2.png`
- `../reports/TC-AUTH-019-round2.png`
- `../reports/TC-AUTH-020-round2.png`
- `../reports/TC-AUTH-022-round2.png`
- `../reports/TC-AUTH-024-round2.png`

