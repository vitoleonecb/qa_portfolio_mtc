## JWT MIDDLEWARE / TOKEN VERIFICATION

### TC-AUTH-003: JWT payload contains expected claims

- **Feature / Requirement:** Token payload structure (`users.js:97–106`)
- **Priority:** P1
- **Preconditions:** Successful login.
- **Test Data:** Any valid credentials.
- **Steps:**
  1. Perform a successful login via API.
  2. Decode the returned JWT.
- **Expected Result:** Payload contains: `user_id`, `email`, `username`, `first_name`, `last_name`, `user_type`, `is_admin` (boolean), `avatar_config` (object or null), `iat`, `exp`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Downstream components (jwtDecode in Settings.jsx, admin checks in WorkshopsPage) depend on all these claims existing. Note: JWT payloads are base64-encoded, not encrypted — PII in claims (email, name, etc.) is readable by anyone with the token. This is standard for JWTs and the token is already visible in the Network tab; the console.log in LogInPage.jsx:52 increases surface area by making it more persistent/scrapable.

- **Actual Result:** Payload contains: `user_id`, `email`, `username`, `first_name`, `last_name`, `user_type`, `is_admin` (boolean), `avatar_config` (object or null), `iat`, `exp`.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`
---

### TC-AUTH-012: Authenticated route rejects request with no token

- **Feature / Requirement:** `verifyToken` in `app.js:71–73` — returns 401 if no `Authorization` header
- **Priority:** P0
- **Preconditions:** N/A.
- **Test Data:** `GET /api/users` with no `Authorization` header.
- **Steps:**
  1. Call any `authenticateToken`-protected route without a token.
- **Expected Result:** 401 response body: `"No Access Token Provided"`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Baseline auth enforcement.

- **Actual Result:** 401 response body: `"No Access Token Provided"`

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`
---

### TC-AUTH-013: Authenticated route rejects request with invalid/tampered token

- **Feature / Requirement:** `jwt.verify` throws → `app.js:104` returns 403
- **Priority:** P0
- **Preconditions:** N/A.
- **Test Data:** `Authorization: Bearer invalidjunktoken`
- **Steps:**
  1. Call a protected route with a garbage token.
- **Expected Result:** 403 with body `"Invalid Token: <jwt error message>"`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Tampering resistance.

- **Actual Result:** 403 is returned in PM2 log without message (noted in TC-AUTH-014)

- **Status:** Inconclusive

- **Evidence:** Screenshot available in `../../reports`
---

### TC-AUTH-014: Authenticated route rejects expired token

- **Feature / Requirement:** JWT `expiresIn: "1h"` — `jwt.verify` rejects expired tokens
- **Priority:** P0
- **Preconditions:** A JWT that was issued > 1 hour ago.
- **Test Data:** Manually craft an expired token, or wait for expiry.
- **Steps:**
  1. Call a protected route with the expired token.
- **Expected Result:** 403 with `"Invalid Token: jwt expired"`.
- **Suggested Automation?** Yes (create token with past `exp`)
- **Notes / Risk Covered:** Session expiry enforcement.

- **Actual Result:** 403 response observed when using expired token. PM2 logs confirm request rejection but do not include response message body. Re-authentication with a new token restores access successfully.

- **Status:** Inconclusive

- **Notes:** PM2 logs do not include response body, which limits debugging visibility. This may be considered an observability improvement rather than a functional defect.

- **Evidence:** Screenshot available in `../../reports`
---

### TC-AUTH-015: Token for deleted user is rejected

- **Feature / Requirement:** `app.js:84–86` — user lookup returns no row → 403 `"Invalid user"`
- **Priority:** P1
- **Preconditions:** A valid JWT for a user who has since been deleted from the DB.
- **Test Data:** JWT with valid signature but `email` not in `users` table.
- **Steps:**
  1. Log in and get a token. Delete the user from DB. Call a protected route.
- **Expected Result:** 403 `"Invalid user"`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Prevents stale tokens from granting access after account removal.

---

### TC-AUTH-016: Admin route rejects non-admin user

- **Feature / Requirement:** `authenticateTokenAdmin` → `requireAdmin && !isAdmin` → 403 (`app.js:91–93`)
- **Priority:** P0
- **Preconditions:** A valid JWT for a regular (non-admin) user.
- **Test Data:** `GET /api/users/list` with a regular user's token.
- **Steps:**
  1. Log in as regular user. Call `/api/users/list`.
- **Expected Result:** 403 `"Access Denied: admin privileges required"`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Privilege escalation prevention.

- **Actual Result:** curl returns 403 `"Access Denied: admin privileges required"`

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`
---

### TC-AUTH-017: Admin route accepts admin user

- **Feature / Requirement:** `authenticateTokenAdmin` passes when `user_type === 'admin'`
- **Priority:** P0
- **Preconditions:** A valid JWT for an admin user.
- **Test Data:** `GET /api/users/list` with admin token.
- **Steps:**
  1. Log in as admin. Call `/api/users/list`.
- **Expected Result:** 200 with list of users.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Happy path for admin access.

- **Actual Result:** 200 with list of users returns after getting accessToken for user with user_type = admin

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`
---

### TC-AUTH-018: `req.user` is populated with fresh DB data, not just token claims

- **Feature / Requirement:** `app.js:79–100` — verifyToken re-queries DB for `user_type`
- **Priority:** P1
- **Preconditions:** User was regular when token was issued, then promoted to admin in DB.
- **Test Data:** JWT with `user_type: "user"`, but DB now has `user_type: "admin"`.
- **Steps:**
  1. Log in as regular user. Promote user to admin in DB directly. Call admin route with same token.
- **Expected Result:** Access is **granted** because `verifyToken` reads from DB, not token claims. `req.user.is_admin` is `true`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** This is a **positive security property** — role changes take effect immediately without re-login. However, it also means a demotion takes effect immediately (verify with reverse scenario).

---
