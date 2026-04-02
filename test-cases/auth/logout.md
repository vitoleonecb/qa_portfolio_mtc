### TC-AUTH-030: Logout clears token and redirects

- **Feature / Requirement:** `Settings.jsx:73–76` — `localStorage.removeItem("accessToken")` then `navigate("/login")`
- **Priority:** P0
- **Preconditions:** User is logged in.
- **Test Data:** N/A.
- **Steps:**
  1. Navigate to `/profile` (Settings page).
  2. Click the Logout button.
- **Expected Result:** `localStorage.accessToken` is removed. User is navigated to `/login`. Avatar icon is no longer shown in header.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Session termination.

- **Actual Result:** accessToken gone, User is redirected to /login and avatar icon is no longer rendered.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`
