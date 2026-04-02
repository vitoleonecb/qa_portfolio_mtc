# BUG-AUTH-001 — Admin Authorization Returns 403 for Valid Credentials

## Summary
Admin-protected endpoints return `403 Forbidden` when accessed with a valid admin JWT, indicating the authorization middleware is not correctly resolving or validating the admin role claim.

---

## Severity
High (P1)

## Priority
P1

## Rationale
Admin functionality is completely inaccessible even with valid credentials, indicating a misconfiguration in role-based access control. This blocks all admin operations and could silently deny legitimate access in production.

---

## Impact
- All admin-protected endpoints are unreachable for authenticated admin users
- Admin operations (e.g., user management, module control) are fully blocked
- Role-based access control is non-functional for the admin tier
- Difficult to distinguish from an actual unauthorized access attempt, making debugging harder

---

## Environment
- Local development
- Node.js / Express
- Auth: JWT-based with role claims
- Tested via: `automation/api/auth/auth_script.py`

---

## Preconditions
- Admin user account exists in the database with the admin role assigned
- Admin user is authenticated and holds a valid JWT

---

## Steps to Reproduce
1. Authenticate as an admin user and obtain a valid JWT
2. Send a request to an admin-protected endpoint with the token in the `Authorization` header:

```bash
curl -X GET http://localhost:3036/api/admin/users \
-H "Authorization: Bearer <admin_token>"
```

3. Observe the response status code

---

## Expected Result
- `200 OK` — admin user is granted access to the protected endpoint

---

## Actual Result
- `403 Forbidden` — access is denied despite valid admin credentials
- Admin operations cannot be performed

---

## Evidence
- API test output from `auth_script.py` showing 403 response for admin-credentialed request
- JWT payload confirms role claim is present in token

---

## Root Cause (Analysis)
The admin authorization middleware appears to not correctly extract or compare the role claim from the JWT payload. Likely causes include:
- Role key mismatch (e.g., reading `role` instead of `user_role`)
- Case sensitivity mismatch (e.g., `"Admin"` vs `"admin"`)
- Middleware not being applied or executed in the correct order

---

## Recommendation
- Audit the admin authorization middleware to verify it correctly reads and validates the role claim from `req.user`
- Add logging to confirm what value is being compared against the expected admin role string
- Add an automated regression test to confirm admin access is granted on a known-good admin account

---

## Notes
This issue was identified during API automation testing (Round 2). Authentication itself succeeds — the JWT is valid and issued correctly. The failure is isolated to authorization enforcement on admin routes.

---

# BUG-MOD-001 — Module Status Endpoint Accepts Invalid Values

## Summary
The module status update endpoint accepts arbitrary values for `newStatus` without validating against the allowed enum values. This allows invalid statuses to be written to the database.

---

## Severity
High (P1)

## Rationale
This issue allows invalid lifecycle states to be persisted, which can lead to inconsistent system behavior across UI rendering, scheduling, and user workflows. While not immediately breaking the application, it introduces a high risk of data integrity issues.

---

## Impact
- Can corrupt module lifecycle state
- Breaks assumptions in UI and backend logic that rely on valid status values
- May cause modules to not render correctly or disappear from expected groupings
- Introduces risk of inconsistent behavior across scheduler, UI, and analytics

---

## Environment
- Local development
- React + Express + MySQL
- Endpoint: `PUT /api/workshops/:workshopid/modules/:moduleid`

---

## Preconditions
- Admin user with valid JWT token
- Existing module in database

---

## Steps to Reproduce
1. Send a PUT request to update module status with an invalid value:

```bash
curl -X PUT http://localhost:3036/api/workshops/50/modules/77 \
-H "Authorization: Bearer <admin_token>" \
-H "Content-Type: application/json" \
-d '{"newStatus":"banana"}'
```

2. Perform a GET request for the same module or refresh the UI.

---

## Expected Result
- API should reject the request with a `400 Bad Request`
- Error message indicating invalid status value
- Database should only allow: `pending`, `open`, `processing`, `completed`

---

## Actual Result
- API returns success response (`200` or `201`)
- Database is updated with invalid value (`"banana"`)
- UI behavior becomes inconsistent or module may not appear in expected status grouping

---

## Evidence
- API response showing successful update with invalid value
- Database query confirming invalid status persisted
- Screenshot: `../reports/TC-MOD-007.png`

---

## Root Cause (Analysis)
The backend does not validate `newStatus` before updating the database. The endpoint directly applies the provided value without checking against the allowed enum set.

---

## Recommendation
- Add backend validation to restrict `newStatus` to allowed enum values
- Return `400 Bad Request` for invalid inputs
- Optionally enforce validation at both API and database layers

---

## Notes
This issue was identified during code review and confirmed through manual API testing.


# BUG-NOTIF-003 — IDOR: Unauthorized Modification of Notification Settings

## Summary
The notification settings update endpoint allows any authenticated user to modify another user's notification settings by supplying a different `user_id` in the request path.

---

## Severity
High (P1)

## Rationale
This is an **Insecure Direct Object Reference (IDOR)** vulnerability. It allows unauthorized modification of user-specific data without proper ownership validation, violating access control principles and exposing user preferences to manipulation.

---

## Impact
- Any authenticated user can modify another user's notification settings
- Users can disable or alter notification channels for other accounts
- Potential for abuse (e.g., silencing notifications, forcing unwanted channels)
- Breaks user data integrity and trust
- Violates basic authorization/security expectations

---

## Environment
- Local development
- Endpoint: `PUT /api/users/:id/notification-settings`
- Auth: JWT (`authenticateToken` middleware)

---

## Preconditions
- User A is authenticated (valid JWT)
- User B exists with a different `user_id`

---

## Steps to Reproduce
1. Authenticate as User A and obtain JWT token
2. Send PUT request targeting another user’s ID:

```bash
curl -X PUT http://localhost:3036/api/users/45/notification-settings \
-H "Authorization: Bearer <UserA_token>" \
-H "Content-Type: application/json" \
-d '{
  "channel": "sms",
  "module_open": true,
  "workshop_rsvp": true,
  "materials_ready": true,
  "showcase_announcements": true,
  "showcase_ticket": false,
  "last_day_reminder": false
}'
```

3. Verify response and database state

---

## Expected Result
- Request is rejected with `403 Forbidden` or `401 Unauthorized`
- Users can only update their own notification settings
- Endpoint enforces ownership validation (`req.user.user_id === id`)

---

## Actual Result
- API returns `200 OK`
- Notification settings for User B are successfully updated by User A
- Database reflects unauthorized changes

---

## Evidence
- API response showing `200 OK`
- Curl request demonstrating cross-user update
- Database snapshot showing modified settings
- Screenshot: `../reports/TC-NOTIF-027.png`

---

## Root Cause (Analysis)
The endpoint uses authentication middleware (`authenticateToken`) but does not validate that the authenticated user owns the resource being modified. There is no check comparing `req.user.user_id` to the `:id` parameter.

---

## Recommendation
- Enforce ownership validation:
```js
if (req.user.user_id !== parseInt(req.params.id)) {
  return res.status(403).json({ error: "Forbidden" });
}
```
- Alternatively, restrict endpoint to admins if cross-user updates are required
- Add automated tests to prevent regression

---

## Notes
This vulnerability is only accessible via API (not exposed in UI), but remains a critical backend security flaw.

