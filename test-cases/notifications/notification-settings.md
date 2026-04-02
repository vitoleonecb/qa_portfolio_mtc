### TC-NOTIF-022: GET notification settings returns stored preferences

- **Feature / Requirement:** `GET /api/users/:id/notification-settings` (`users.js:457–475`)
- **Priority:** P0
- **Preconditions:** Authenticated user with stored notification settings.
- **Test Data:** User with `{ channel: "email", module_open: true, last_day_reminder: false, ... }`.
- **Steps:**
  1. Call `GET /api/users/:id/notification-settings`.
- **Expected Result:** 200 with the parsed JSON settings object.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Happy path for settings retrieval.

- **Actual Result:** 200 with the parsed JSON settings object matching that of JSON stored in DB.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-NOTIF-023: GET notification settings for non-existent user returns 404

- **Feature / Requirement:** `users.js:465`
- **Priority:** P2
- **Preconditions:** Authenticated user with valid token.
- **Test Data:** `id = 99999`.
- **Steps:**
  1. Call `GET /api/users/99999/notification-settings`.
- **Expected Result:** 404 `{ error: "User not found" }`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Negative path.

---

### TC-NOTIF-024: PUT notification settings — valid channel values

- **Feature / Requirement:** `PUT /api/users/:id/notification-settings` (`users.js:477–506`)
- **Priority:** P0
- **Preconditions:** Authenticated user.
- **Test Data:** `{ channel: "sms", module_open: true, last_day_reminder: false, materials_ready: true, workshop_rsvp: true, showcase_announcements: true, showcase_ticket: false }`
- **Steps:**
  1. Call PUT with valid payload.
- **Expected Result:** 200 `{ ok: true }`. DB updated.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Happy path for settings update.

- **Actual Result:** 200 `{ ok: true }`. DB updated.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-NOTIF-025: PUT notification settings — rejects invalid channel

- **Feature / Requirement:** `users.js:484–487` — validates against `['none', 'email', 'sms', 'both']`
- **Priority:** P1
- **Preconditions:** Authenticated user.
- **Test Data:** `{ channel: "telegram" }`
- **Steps:**
  1. Call PUT with invalid channel.
- **Expected Result:** 400 `{ error: "Invalid channel value" }`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Input validation.

- **Actual Result:** 400 `{ error: "Invalid channel value" }`.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-NOTIF-026: PUT notification settings — rejects non-boolean sub-options

- **Feature / Requirement:** `users.js:490–495` — type check on boolean keys
- **Priority:** P1
- **Preconditions:** Authenticated user.
- **Test Data:** `{ channel: "email", module_open: "yes" }`
- **Steps:**
  1. Call PUT with string value for a boolean field.
- **Expected Result:** 400 `{ error: "module_open must be a boolean" }`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Type validation.

- **Actual Result:** 400 `{ error: "module_open must be a boolean" }`.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-NOTIF-027: PUT notification settings — does not validate user owns the ID

- **Feature / Requirement:** `users.js:478` — uses `authenticateToken` but does NOT check `req.user.user_id === id`
- **Priority:** P1 (Security)
- **Preconditions:** User A is authenticated. User B exists with a different ID.
- **Test Data:** User A calls `PUT /api/users/<UserB_id>/notification-settings`.
- **Steps:**
  1. Log in as User A. Call PUT with User B's ID.
- **Expected Result:** Request is rejected with 403 Forbidden or 401 Unauthorized. Authenticated users should only be able to update their own notification settings.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** **Bug/Security issue:** Any authenticated user can modify any other user's notification settings via the API. The endpoint only checks authentication, not ownership.

- **Actual Result:** Request returned 200 OK. User A was able to successfully update User B's notification settings via the API. Database reflects updated values for User B.

- **Status:** Fail

- **Evidence:** Screenshot available in `../../reports`

---

### TC-NOTIF-028: Registration defaults to email-only notifications with all sub-options on

- **Feature / Requirement:** `RegistrationPage.jsx:59–67` — `DEFAULT_NOTIF_SETTINGS`
- **Priority:** P1
- **Preconditions:** On registration page, at the notifications step.
- **Test Data:** N/A.
- **Steps:**
  1. Progress to the notification preferences step.
- **Expected Result:** Master toggle is ON. Text updates toggle is OFF. Channel is `email`. All 6 sub-options are toggled ON.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Default state differs from DB migration default (`both`) and Settings page default (`none`). See risks.

---

### TC-NOTIF-029: Registration requires phone number when text updates are enabled

- **Feature / Requirement:** `RegistrationPage.jsx:275–281` — `validatePhone` called when channel is `sms` or `both`
- **Priority:** P1
- **Preconditions:** User enables text updates on the notification step.
- **Test Data:** Toggle text updates ON, leave phone blank or enter `"123"`.
- **Steps:**
  1. Enable text updates. Leave phone blank. Click Next.
  2. Enter `"123"`. Click Next.
- **Expected Result:**
  - Blank phone: no error (phone is optional per `validatePhone`, returns `''` for empty).
  - `"123"`: error "Please enter a valid 10-digit phone number".
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Phone validation only fires when channel includes SMS. Empty phone is allowed, which means a user with `channel = 'both'` but no phone gets email-only silently.

---

### TC-NOTIF-030: Registration notification settings are saved with the user record

- **Feature / Requirement:** `RegistrationPage.jsx:116–127` — `notification_settings: notifSettings` sent in POST body; `users.js:273` — inserted as JSON
- **Priority:** P0
- **Preconditions:** N/A.
- **Test Data:** Custom notification settings (e.g., toggle off `materials_ready`).
- **Steps:**
  1. During registration, toggle off "Materials ready".
  2. Complete registration.
  3. Verify via `GET /api/users/:id/notification-settings`.
- **Expected Result:** Settings persisted with `materials_ready: false` and other values as configured.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** End-to-end settings persistence from registration.

- **Actual Result:** Settings persisted with `materials_ready: false` and other values as configured.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---
### TC-NOTIF-031: Settings page loads saved notification preferences on mount

- **Feature / Requirement:** `Settings.jsx:56–68` — fetches from `GET /notification-settings`
- **Priority:** P0
- **Preconditions:** User logged in. Has custom notification settings.
- **Test Data:** User with `channel = "sms"`, `module_open = false`.
- **Steps:**
  1. Navigate to `/profile`.
- **Expected Result:** Master toggle is ON. Channel selector shows "Text only". Module opened toggle is OFF.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Correct hydration of saved state.

- **Actual Result:** Refreshed the /Profile page: Master toggle is ON. Channel selector shows "Text only". Module opened toggle is OFF.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-NOTIF-032: Settings page master toggle disables all notifications

- **Feature / Requirement:** `Settings.jsx:98–99` — toggles between `none` and `email`
- **Priority:** P0
- **Preconditions:** Notifications currently enabled.
- **Test Data:** N/A.
- **Steps:**
  1. Click master toggle to OFF.
- **Expected Result:** Channel set to `none`. PUT fires immediately. Sub-option toggles hidden. No notifications will be delivered.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Immediate persistence via `persistSettings`.

- **Actual Result:** Channel set to `none`. PUT fires immediately. Sub-option toggles hidden. No notifications will be delivered.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-NOTIF-033: Settings page delivery channel cycles through email → sms → both

- **Feature / Requirement:** `Settings.jsx:102–106` — `cycleChannel`
- **Priority:** P1
- **Preconditions:** Notifications enabled, channel starts at `email`.
- **Test Data:** N/A.
- **Steps:**
  1. Click "Email only" button → changes to "Text only".
  2. Click again → changes to "Email & Text".
  3. Click again → back to "Email only".
- **Expected Result:** Each click advances through `["email", "sms", "both"]` cycle. PUT fires on each change.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** UI matches the three valid channel values.

---

### TC-NOTIF-034: Settings page individual sub-option toggles persist immediately

- **Feature / Requirement:** `Settings.jsx:90–96, 192–200`
- **Priority:** P1
- **Preconditions:** Notifications enabled.
- **Test Data:** N/A.
- **Steps:**
  1. Toggle "Materials ready" OFF.
  2. Reload the page.
- **Expected Result:** "Materials ready" is OFF after reload. PUT was fired on toggle. Backend has `materials_ready: false`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Each toggle immediately persists via PUT, no save button needed.

---
