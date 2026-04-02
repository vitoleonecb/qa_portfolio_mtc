### TC-AUTH-027: Confirm email — valid token

- **Feature / Requirement:** `GET /api/users/confirm-email?token=<valid>` (`users.js:135–154`)
- **Priority:** P1
- **Preconditions:** User registered but `email_verified = FALSE`. Have a valid `email_confirm` JWT.
- **Test Data:** Valid token.
- **Steps:**
  1. Navigate to `/confirm-email?token=<valid>`.
- **Expected Result:**
  - DB updated: `email_verified = TRUE`.
  - Page shows "Your email has been confirmed!" with a "Log In" button.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Happy path email confirmation.

- **Actual Result:** DB updated: `email_verified = TRUE`. Page shows "Your email has been confirmed!" with a "Log In" button.

- **Status**: Pass
---

### TC-AUTH-028: Confirm email — expired/invalid token

- **Feature / Requirement:** Tokens expire in 24h. Invalid token → 400.
- **Priority:** P1
- **Preconditions:** An expired or invalid token.
- **Test Data:** Expired `email_confirm` token.
- **Steps:**
  1. Navigate to `/confirm-email?token=<expired>`.
- **Expected Result:** Page shows error message. Resend form is rendered below with email input and "Resend" button.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Expired link recovery path.

---

### TC-AUTH-029: Resend confirmation email — valid flow

- **Feature / Requirement:** `POST /api/users/resend-confirm-email` (`users.js:307–339`)
- **Priority:** P2
- **Preconditions:** User exists with `email_verified = FALSE`.
- **Test Data:** User's email.
- **Steps:**
  1. On the error state of confirm-email page, enter email and click "Resend".
- **Expected Result:** API returns 200 `{ ok: true }`. Page shows "If that email is in our system, a new confirmation link has been sent."
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** The response is always 200 regardless of whether the email exists or is already verified — prevents enumeration.

---
