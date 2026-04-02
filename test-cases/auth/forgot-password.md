
### TC-AUTH-019: Forgot password — valid email sends reset link

- **Feature / Requirement:** `POST /api/users/forgot-password` (`users.js:342–371`)
- **Priority:** P0
- **Preconditions:** User with `test12@test.com` exists.
- **Test Data:** `{ email: "test12@test.com" }`
- **Steps:**
  1. On login page, click "Forgot Password?".
  2. Enter `test@example.com`. Submit.
- **Expected Result:**
  - API returns 200 `{ ok: true }`.
  - A `resetPassword` job is enqueued in `notificationQueue`.
  - Frontend shows "Check your email for a reset link".
- **Suggested Automation?** Partial (API yes, email delivery no)
- **Notes / Risk Covered:** Happy path for password recovery.

- **Actual Result:** - API returned 200, but no resetPassword enqueue evidence was captured in logs; queue verification not yet performed

- **Status:** Inconclusive / Lacking queue evidence

---

### TC-AUTH-020: Forgot password — non-existent email still returns 200

- **Feature / Requirement:** `users.js:353` — `if (!user) return res.status(200)` to prevent email enumeration
- **Priority:** P1
- **Preconditions:** No user with `nobody@example.com`.
- **Test Data:** `{ email: "nobody@example.com" }`
- **Steps:**
  1. Enter non-existent email in forgot password form. Submit.
- **Expected Result:** 200 `{ ok: true }`. Frontend shows success message. No notification is queued.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** User enumeration prevention — critical security behavior.

- **Actual Result:** API returned 200 with no response body. Front end displayed “Check your email for a reset link” after submission. No resetPassword queue activity was observed, but queue logging/verification is not currently implemented for resetting passwords.

- **Status:** Inconclusive / Queue assertion not directly verified

---

### TC-AUTH-021: Forgot password — frontend validates email format

- **Feature / Requirement:** `LogInPage.jsx:68` calls `validateEmail(forgotEmail)` before API call
- **Priority:** P2
- **Preconditions:** On forgot password sub-form.
- **Test Data:** `"notanemail"`
- **Steps:**
  1. Enter `"notanemail"` in the forgot password email field. Submit.
- **Expected Result:** Error "Please enter a valid email address" displayed. No API call.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Client-side validation guard.

---

### TC-AUTH-022: Reset password — valid token and strong password

- **Feature / Requirement:** `POST /api/users/reset-password` (`users.js:375–431`)
- **Priority:** P0
- **Preconditions:** A valid `password_reset` JWT token.
- **Test Data:** `{ token: "<valid>", newPassword: "NewStrong1!" }`
- **Steps:**
  1. Navigate to `/reset-password?token=<valid>`.
  2. Enter new password and confirm it. Submit.
- **Expected Result:**
  - Password is updated (bcrypt-hashed) in DB.
  - Response includes a new `accessToken` for auto-login.
  - `localStorage.accessToken` is set.
  - User is navigated to `/showcases`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Full password reset + auto-login flow.

- **Actual Result:** 
  - Password hash updated in DB for the correct user (verified via direct query; hash differs from pre-reset value)
  - No Server-side instrumentation confirming new accessToken was regenerated for auto-login
  - `localStorage.accessToken` populated after request
  - User redirected to `/showcases`

- **Status:** Inconclusive - lacking server side logging to confirm source of new accessToken generation for auto log in
---

### TC-AUTH-023: Reset password — expired token

- **Feature / Requirement:** Reset tokens expire in 1h (`users.js:358`)
- **Priority:** P1
- **Preconditions:** An expired `password_reset` token.
- **Test Data:** Expired token.
- **Steps:**
  1. Navigate to `/reset-password?token=<expired>`.
  2. Enter new password and submit.
- **Expected Result:** 400 `{ error: "Invalid or expired token: jwt expired" }`. Frontend shows the error. Password is not changed.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Token expiry enforcement.

- **Actual Result:** Server returned 400, front end UI rendered an error message saying: "Invalid or expired token: jwt expired".

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-AUTH-024: Reset password — token with wrong `type` claim rejected

- **Feature / Requirement:** `users.js:383–385` — checks `decoded.type !== 'password_reset'`
- **Priority:** P1
- **Preconditions:** A valid JWT but with `type: 'email_confirm'`.
- **Test Data:** Use an email confirmation token as the reset token.
- **Steps:**
  1. Call `POST /api/users/reset-password` with an `email_confirm` token.
- **Expected Result:** 400 `{ error: "Invalid token type" }`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Cross-purpose token reuse prevention.

- **Actual Result:** API returned 400, UI displayed error state, Specific error message ("Invalid token type") not verified via response body or logs

- **Status:** Inconclusive (error reason not directly verified)
---

### TC-AUTH-025: Reset password — missing token in URL shows error

- **Feature / Requirement:** `ResetPasswordPage.jsx:18–25` — renders "Invalid or missing reset link" if `!token`
- **Priority:** P2
- **Preconditions:** N/A.
- **Test Data:** Navigate to `/reset-password` with no `?token=` param.
- **Steps:**
  1. Navigate to `/reset-password` (no query string).
- **Expected Result:** Page displays "Invalid or missing reset link." No form fields shown.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Edge case UX.

---

### TC-AUTH-026: Reset password — frontend validates password complexity

- **Feature / Requirement:** `ResetPasswordPage.jsx:30–37` uses `validatePassword` and `validateConfirmPassword`
- **Priority:** P1
- **Preconditions:** On reset password page with valid token.
- **Test Data:** `"short"` (too short), `"alllowercase1!"` (no uppercase), mismatched confirm.
- **Steps:**
  1. Enter `"short"` → submit → expect "Password must be at least 8 characters".
  2. Enter `"alllowercase1!"` → expect "Password must contain at least one uppercase letter".
  3. Enter valid password, mismatched confirm → expect "Passwords do not match".
- **Expected Result:** Field-level errors are shown. No API call on validation failure.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Validation rules: ≥8 chars, ≤128 chars, uppercase, lowercase, digit, special char, match confirm.

- **Actual Result:** Field-level errors are shown. No API call on validation failure.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---
