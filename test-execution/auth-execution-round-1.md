# Auth Test Execution — Round 1

## Overview
This document summarizes the first round of manual test execution for authentication features.

- Total Test Cases (in scope for Round 1): 28
- Executed: 28
- Passed: 22
- Failed: 0
- Inconclusive: 6
- Blocked: 0

- Execution Rate: 100%
- Pass Rate: 78.6%

---

## Scope Covered
- Login (valid, invalid, validation)
- JWT issuance and protected route enforcement
- Admin vs. non-admin authorization
- Registration and auto-login
- Logout and session cleanup
- Forgot password and reset password flows
- Email confirmation
- UI auth state (logged-in vs. logged-out)

---

## Execution Summary

| Test ID | Title | Status | Notes |
|--------|------|--------|------|
| TC-AUTH-001 | Valid login (email) | Pass | Token stored, redirect to Showcases page successful |
| TC-AUTH-002 | Valid login (username) | Pass | Token stored, redirect to Showcases page successful |
| TC-AUTH-005 | Login fails with wrong password | Pass | No token set, API returns 401, accessToken not set |
| TC-AUTH-006 | Login fails with wrong username | Pass | API returns 401, accessToken not set, front end error same as wrong password |
| TC-AUTH-007 | Login with empty email field — frontend validation | Pass | No API requests made, front end error message asking for username or email |
| TC-AUTH-008 | Login with empty password field — frontend validation | Pass | No API requests made, front end error message asking for password |
| TC-AUTH-009 | Login with both fields empty — backend validation | Pass | API returns "Email/username and password are required." |
| TC-AUTH-011 | Login handles non-401 server errors gracefully | Pass | Frontend shows "Something went wrong. Please try again." |
| TC-AUTH-003 | JWT payload contains expected claims | Pass | The decoded accessToken contains the expected claims; Should ensure console is not logging this for prod |
| TC-AUTH-012 | Authenticated route rejects request with no token | Pass | 401 response body: "No Access Token Provided". |
| TC-AUTH-030 | Logout clears token and redirects | Pass | Token was cleared, user redirected to /login, avatar hidden |
| TC-AUTH-014 | Authenticated route rejects expired token | Inconclusive | PM2 Logs show 403, but no message body, and some UI remain in authenticated state, no automatic logout |
| TC-AUTH-013 | Authenticated route rejects request with invalid/tampered token | Inconclusive | PM2 Logs show 403, but no message body |
| TC-AUTH-016 | Admin route rejects non-admin user | Pass | curl returns 403 "Access Denied: admin privileges required" |
| TC-AUTH-017 | Admin route accepts admin user | Pass | 200 with list of users returns after getting accessToken for user with user_type = admin |
| TC-AUTH-033 | Successful registration auto-logs in | Pass | User is registered, then automatically logged in (token stored in localStorage). Success overlay is shown. Clicking "Go to Showcases" navigates to /showcases. |
| TC-AUTH-019 | Forgot password — valid email sends reset link | Inconclusive (Queue side-effect not verifiable) | API returned 200, but no resetPassword enqueue evidence was captured in logs; queue verification not yet performed |
| TC-AUTH-020 | non-existent email still returns 200 | Inconclusive (Queue side-effect not verifiable) | API returned 200 with no response body. Front end displayed “Check your email for a reset link” after submission. No resetPassword queue activity was observed, but queue logging/verification is not currently implemented for reseting passwords. |
| TC-AUTH-022 | Reset password — valid token and strong password | Inconclusive (Queue side-effect not verifiable) | API returned 200 with no response body. Front end displayed “Check your email for a reset link” after submission. No resetPassword queue activity was observed, but queue logging/verification is not currently implemented for reseting passwords. |
| TC-AUTH-023 | Reset password — expired token | Pass | Server returned 400, front end UI rendered an error message saying: "Invalid or expired token: jwt expired". |
| TC-AUTH-024 | Reset password — token with wrong type claim rejected | Inconclusive | Server returned 400, front end UI rendered an error message saying: "Invalid or expired token: jwt expired". But error message doesn't confirm reason for rejection |
| TC-AUTH-026 | Reset password — frontend validates password complexity | Pass | Field-level errors are shown. No API call on validation failure. |
| TC-AUTH-027 | Confirm email — valid token | Pass | DB updated: email_verified = TRUE. Page shows "Your email has been confirmed!" with a "Log In" button. |
| TC-AUTH-031 | Root layout hides avatar when not logged in | Pass | AccountAvatarButton is not rendered in the header when there is no access token in local storage. |
| TC-AUTH-032 | Settings page redirects unauthenticated user to login | Pass | User is immediately redirected to /login when no accessToken for user when attempting to naviate to /profile. |
---

## Key Findings

### Bugs and Improvements Identified
1. **TC-AUTH-014 — Observability Gap**
   - PM2 logs did not include response message body for expired token requests
   - **Impact:** Unable to verify error payload via server logs
   - **Recommendation:** Add structured logging for response bodies (excluding sensitive data) to improve verification

2. **TC-AUTH-014 — BUG: Auth State Not Invalidated**
   - UI maintains authenticated state after token expiration (401 response)
   - **Impact:** User remains in invalid session; potential security/UX issue
   - **Recommendation:** Implement global 401 interceptor to clear auth state and redirect to login

3. **TC-AUTH-033 — UI Consistency Issue**
   - “Go to Showcases” button displays default browser focus ring, inconsistent with rest of UI
   - **Impact:** Inconsistent user experience and accessibility styling
   - **Recommendation:** Implement standardized `:focus-visible` styles across components

4. **TC-AUTH-019 — Observability Gap (Queue Verification)**
   - Forgot password endpoint returned 200, but no resetPassword enqueue evidence present in logs
   - **Impact:** Unable to confirm async job creation
   - **Recommendation:** Add instrumentation around `notificationQueue.add()` to log job creation (e.g., jobId, userId)

5. **TC-AUTH-022 — Observability Gap (Resolved)**
   - Initial execution lacked visibility into API response payload (accessToken not directly verifiable)
   - **Action Taken:** Added server-side instrumentation to log presence of accessToken in response
   - **Outcome:** Subsequent verification confirmed token issuance
---

## Risks Identified
- No refresh token handling
- JWT contains user data
- Lack of Message Bodies in Server Logs
- Without sufficient server logging, failed email jobs for example could silently break password recovery

---

## Evidence
- `../../reports/TC-AUTH-001.png`
- `../../reports/TC-AUTH-002.png`
- `../../reports/TC-AUTH-003.png`
- `../../reports/TC-AUTH-005-console.png`
- `../../reports/TC-AUTH-005-storage.png`
- `../../reports/TC-AUTH-006.png`
- `../../reports/TC-AUTH-007.png`
- `../../reports/TC-AUTH-008.png`
- `../../reports/TC-AUTH-009.png`
- `../../reports/TC-AUTH-011.png`
- `../../reports/TC-AUTH-013.png`
- `../../reports/TC-AUTH-014.png`
- `../../reports/TC-AUTH-016.png`
- `../../reports/TC-AUTH-017.png`
- `../../reports/TC-AUTH-019.png`
- `../../reports/TC-AUTH-020.png`
- `../../reports/TC-AUTH-022.png`
- `../../reports/TC-AUTH-023.png`
- `../../reports/TC-AUTH-024.png`
- `../../reports/TC-AUTH-026.png`
- `../../reports/TC-AUTH-027.png`
- `../../reports/TC-AUTH-030.png`
- `../../reports/TC-AUTH-031.png`
- `../../reports/TC-AUTH-033.png`

---

## Next Steps
- Round 2 execution after observability improvements are implemented
- Execute remaining auth test cases not covered in Round 1
- Begin automation for high-value regression flows (login, protected routes, logout)
