## LOGIN — Happy Path

---

### TC-AUTH-001: Successful login with email

- **Feature / Requirement:** `POST /api/users/login` — email-based authentication
- **Priority:** P0 (Critical)
- **Preconditions:** A registered user exists with email `test@example.com` and a known bcrypt-hashed password.
- **Test Data:** `{ email: "test@example.com", password: "ValidPass1!" }`
- **Steps:**
  1. Navigate to `/login`.
  2. Enter `test@example.com` in the "Email or Username" field.
  3. Enter `ValidPass1!` in the "Password" field.
  4. Click the Log In button (or press Enter).
- **Expected Result:**
  - API returns 200 with `{ message: "Login successful", accessToken: "<JWT>", user: { user_id, email, username, first_name, last_name, user_type, is_admin, avatar_config } }`.
  - `localStorage.accessToken` is set.
  - User is navigated to `/showcases`.
  - No error message displayed.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Core happy path. Verifies JWT issuance, localStorage write, and redirect target.

- **Actual Result:** User navigated to Showcases page, console shows 200 returned, no error message.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`
---

### TC-AUTH-002: Successful login with username

- **Feature / Requirement:** `POST /api/users/login` — username-based login (backend queries `WHERE email = ? OR username = ?`)
- **Priority:** P0
- **Preconditions:** A registered user with username `testuser123` exists.
- **Test Data:** `{ username: "testuser123", password: "ValidPass1!" }`
- **Steps:**
  1. Navigate to `/login`.
  2. Enter `testuser123` in the "Email or Username" field.
  3. Enter valid password and submit.
- **Expected Result:** 200 response, token stored, navigated to `/showcases`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** The frontend sends the value as `email` in the payload body regardless of whether it's an email or username — backend handles the OR lookup.

- **Actual Result:** User navigated to Showcases page, console shows 200 returned, no error message.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`
---

### TC-AUTH-004: Login trims whitespace from email/username input

- **Feature / Requirement:** Frontend sends `emailOrUsername.trim()` (`LogInPage.jsx:50`)
- **Priority:** P2
- **Preconditions:** Registered user `test@example.com`.
- **Test Data:** `"  test@example.com  "`
- **Steps:**
  1. Enter `"  test@example.com  "` (leading/trailing spaces) and valid password.
  2. Submit.
- **Expected Result:** Login succeeds (frontend trims before sending).
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** UX edge case — copy-paste from email clients often includes trailing spaces.

---

## LOGIN — Negative / Validation

---

### TC-AUTH-005: Login fails with wrong password

- **Feature / Requirement:** bcrypt compare failure → 401
- **Priority:** P0
- **Preconditions:** Registered user exists.
- **Test Data:** Correct email, wrong password.
- **Steps:**
  1. Enter valid email and incorrect password.
  2. Submit.
- **Expected Result:**
  - API returns 401 `{ message: "Invalid email/username or password." }`.
  - Frontend displays "Invalid email/username or password".
  - `localStorage.accessToken` is NOT set.
  - User remains on `/login`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** The error message is intentionally vague (does not reveal whether email exists) — verify this.

- **Actual Result:** API returns 401, frontend error message: "Invalid email/username or password", `localStorage.accessToken` is NOT set, User remains on `/login`

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-AUTH-006: Login fails with non-existent email/username

- **Feature / Requirement:** User lookup returns no rows → 401
- **Priority:** P0
- **Preconditions:** No user with email `ghost@example.com` exists.
- **Test Data:** `{ email: "ghost@example.com", password: "anything" }`
- **Steps:**
  1. Enter non-existent email and any password.
  2. Submit.
- **Expected Result:** 401 with message `"Invalid email/username or password."` — same message as wrong-password to prevent user enumeration.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** User enumeration prevention.

- **Actual Result:** 401 with message `"Invalid email/username or password."` — same message as wrong-password to prevent user enumeration.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-AUTH-007: Login with empty email field — frontend validation

- **Feature / Requirement:** `LogInPage.jsx:39–42` checks `!emailOrUsername.trim()`
- **Priority:** P1
- **Preconditions:** On login page.
- **Test Data:** Email field empty, password field populated.
- **Steps:**
  1. Leave email/username blank. Enter a password. Submit.
- **Expected Result:** Error message "Please enter your email or username" displayed. No API call made.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Client-side guard before network request.

- **Actual Result:** No API call made. Error message "Please enter your email or username" displayed.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-AUTH-008: Login with empty password field — frontend validation

- **Feature / Requirement:** `LogInPage.jsx:43–46` checks `!password`
- **Priority:** P1
- **Preconditions:** On login page.
- **Test Data:** Email populated, password empty.
- **Steps:**
  1. Enter an email. Leave password empty. Submit.
- **Expected Result:** Error message "Please enter your password" displayed. No API call made.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Client-side guard.

- **Actual Result:** No API call made. Error message "Please enter your password" displayed.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-AUTH-009: Login with both fields empty — backend validation

- **Feature / Requirement:** `users.js:60–62` — returns 400 if `!email || !password`
- **Priority:** P1
- **Preconditions:** N/A (API-level test).
- **Test Data:** `POST /api/users/login` with `{ email: "", password: "" }` or missing body fields.
- **Steps:**
  1. Send POST directly to API with empty/missing email and password.
- **Expected Result:** 400 `{ message: "Email/username and password are required." }`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Backend defense-in-depth. Frontend guards exist but API must reject independently.

- **Actual Result:** API returns "Email/username and password are required."

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-AUTH-010: Error message clears on input change

- **Feature / Requirement:** `LogInPage.jsx:21,26` — `if (error) setError('')` on keystroke
- **Priority:** P2
- **Preconditions:** An error message is currently displayed on the login form.
- **Test Data:** N/A.
- **Steps:**
  1. Trigger an error (e.g., submit empty form).
  2. Type any character in either the email or password field.
- **Expected Result:** Error message disappears immediately.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** UX polish.

---

### TC-AUTH-011: Login handles non-401 server errors gracefully

- **Feature / Requirement:** `LogInPage.jsx:59–61` — catch-all for non-401 errors
- **Priority:** P2
- **Preconditions:** Backend is down or returns 500.
- **Test Data:** Valid credentials but backend unreachable or DB down.
- **Steps:**
  1. Attempt login when backend is unavailable.
- **Expected Result:** Frontend shows "Something went wrong. Please try again." (not a raw error or blank screen).
- **Suggested Automation?** No (requires infrastructure manipulation)
- **Notes / Risk Covered:** Resilience / graceful degradation.

- **Actual Result:** Frontend shows "Something went wrong. Please try again."

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`
