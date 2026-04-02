### TC-AUTH-031: Root layout hides avatar when not logged in

- **Feature / Requirement:** `Root.jsx:30–31` — `isLoggedIn = !!localStorage.getItem('accessToken')`
- **Priority:** P2
- **Preconditions:** No `accessToken` in localStorage.
- **Test Data:** N/A.
- **Steps:**
  1. Clear localStorage. Navigate to `/login` or `/`.
- **Expected Result:** `AccountAvatarButton` is NOT rendered in the header.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** UI state consistency.

- **Actual Result:** AccountAvatarButton is not rendered in the header when there is no access token in local storage.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-AUTH-032: Settings page redirects unauthenticated user to login

- **Feature / Requirement:** `Settings.jsx:37` — `if (!accessToken) { navigate("/login"); return; }`
- **Priority:** P1
- **Preconditions:** No token in localStorage.
- **Test Data:** N/A.
- **Steps:**
  1. Navigate directly to `/profile` without being logged in.
- **Expected Result:** User is immediately redirected to `/login`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Only Settings implements this guard — see "Questions / Risks" below.

- **Actual Result:** User is immediately redirected to `/login` when no accessToken for user when attempting to naviate to `/profile`.

- **Status:** Pass
