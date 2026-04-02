### TC-MOD-001: Admin creates a module via the UI

- **Feature / Requirement:** `POST /api/workshops/:workshopid/modules` (admin-only, `workshops.js:659–669`)
- **Priority:** P0
- **Preconditions:** Admin user logged in. Workshop exists. On the `WorkshopModules` page.
- **Test Data:** Module name: `"Module A"` (≤20 chars)
- **Steps:**
  1. Click the "Create" button.
  2. Enter `"Module A"` in the module name input.
  3. Press Enter.
- **Expected Result:**
  - 201 response from API.
  - Module appears in the "Pending" section of the page.
  - Module status is `pending`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** The input has `maxLength={20}` on the frontend (`WorkshopModules.jsx:592`). Backend has NO length validation — only frontend enforces it.

- **Actual Result:** 201 response from API, Module appears under "Pending" section of the page and it is of status "Pending". Code review showed there is no length validation but this will be a lower priority validation gap to address later.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-MOD-002: Non-admin user cannot see the Create button

- **Feature / Requirement:** `WorkshopModules.jsx:581` — `{isAdmin && <CreateButton />}`
- **Priority:** P0
- **Preconditions:** Regular user logged in.
- **Test Data:** N/A
- **Steps:**
  1. Navigate to a workshop's module page.
- **Expected Result:** "Create" button is NOT rendered. No way to create a module from the UI.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** UI-level guard. Backend also enforces via `authenticateTokenAdmin`.

---

### TC-MOD-003: Non-admin API call to create module is rejected

- **Feature / Requirement:** `authenticateTokenAdmin` middleware on `POST /:workshopid/modules`
- **Priority:** P0
- **Preconditions:** Regular user token.
- **Test Data:** `POST /api/workshops/1/modules` with `{ workshop_module_name: "test" }` using regular user bearer token.
- **Steps:**
  1. Call the API directly with a non-admin token.
- **Expected Result:** 403 `"Access Denied: admin privileges required"`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Backend authorization enforcement.

- **Actual Result:** 403 `"Access Denied: admin privileges required"`.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-MOD-004: Module created with empty name

- **Feature / Requirement:** Backend does not validate empty module name.
- **Priority:** P1
- **Preconditions:** Admin user.
- **Test Data:** `{ workshop_module_name: "" }`
- **Steps:**
  1. Call `POST /api/workshops/:id/modules` with empty name (or submit empty field from UI).
- **Expected Result:** Backend accepts the insert — module is created with empty/null name. **This is a gap.** Frontend input allows submitting empty on Enter key press; there's no `trim()` check.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Missing validation. The frontend input has no `required` attribute and `handleSubmit` doesn't check if `moduleName` is empty.

---

### TC-MOD-005: Module delete by admin

- **Feature / Requirement:** `DELETE /api/workshops/:workshopid/modules/:moduleid` (`workshops.js:672–686`)
- **Priority:** P1
- **Preconditions:** Admin token. Module exists.
- **Test Data:** Valid `moduleid`.
- **Steps:**
  1. Call DELETE endpoint.
- **Expected Result:** 201 `"Module Successfully Deleted"`. Module no longer appears in subsequent GET calls.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Uses `moduleExists.length === 1` check — if module doesn't exist returns 404.

---

### TC-MOD-006: Delete non-existent module returns 404

- **Feature / Requirement:** `workshops.js:681`
- **Priority:** P2
- **Preconditions:** Admin token.
- **Test Data:** `moduleid = 99999` (doesn't exist).
- **Steps:**
  1. Call `DELETE /api/workshops/1/modules/99999`.
- **Expected Result:** 404 `"Module Doesn't exist"`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Negative path.

---
