### TC-AUTH-033: Successful registration auto-logs in

- **Feature / Requirement:** `RegistrationPage.jsx:132–137` — immediately calls login after registration
- **Priority:** P0
- **Preconditions:** N/A.
- **Test Data:** Fresh user data.
- **Steps:**
  1. Complete all registration steps.
  2. Submit final step.
- **Expected Result:** User is registered, then automatically logged in (token stored in localStorage). Success overlay is shown. Clicking "Go to Showcases" navigates to `/showcases`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Two sequential API calls (register then login) — verify both succeed atomically from the user's perspective.

- **Actual Result:** User is registered, then automatically logged in (token stored in localStorage). Success overlay is shown. Clicking "Go to Showcases" navigates to `/showcases`.

- **Status:** Pass

- **Notes:** The "Go to Showcases" button had the browsers default focus ring which is not found anywhere else in the UI and may reveal inconsistency in UI style.
