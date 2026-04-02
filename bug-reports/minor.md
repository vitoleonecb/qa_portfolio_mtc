# BUG-AUTH-002 — Admin Endpoints Return Plain Text Instead of JSON

## Summary
Admin-protected endpoints return a plain text response body instead of a JSON-formatted response, causing client-side JSON parsing failures when attempting to process the response.

---

## Severity
Medium (P2)

## Priority
P2

## Rationale
While this does not expose a security risk or break core business logic, it violates the API contract expected by clients and causes test failures. It also indicates a lack of consistency in response formatting across admin routes.

---

## Impact
- `resp.json()` throws a parsing exception in API clients and automated tests
- Clients cannot programmatically process admin endpoint responses
- Inconsistent with all other API responses, breaking the expected contract
- May mask the underlying 403 issue (BUG-AUTH-001) by making errors harder to inspect

---

## Environment
- Local development
- Node.js / Express
- Auth: JWT-based
- Tested via: `automation/api/auth/auth_script.py`

---

## Preconditions
- Request sent to an admin-protected endpoint
- Endpoint returns any response (regardless of status code)

---

## Steps to Reproduce
1. Send a request to any admin-protected endpoint (e.g., `GET /api/admin/users`)
2. Attempt to parse the response body as JSON:

```python
resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
data = resp.json()  # raises JSONDecodeError
```

3. Observe the exception

---

## Expected Result
- All API responses return `Content-Type: application/json` with a valid JSON body
- `resp.json()` succeeds without error

---

## Actual Result
- Response body is plain text (e.g., `"Forbidden"` or `"Unauthorized"`)
- `resp.json()` raises a `JSONDecodeError`
- `Content-Type` header does not specify `application/json`

---

## Evidence
- API test output from `auth_script.py` showing `JSONDecodeError` on admin endpoint response
- Raw response body is plain text string

---

## Root Cause (Analysis)
Admin route handlers (or the authorization middleware rejecting the request) are returning plain text strings instead of using `res.json()`. This is likely in the error-handling path of the admin middleware.

---

## Recommendation
- Update all admin route handlers and middleware rejection responses to use `res.json()`:
```js
return res.status(403).json({ error: "Forbidden" });
```
- As a short-term workaround in tests, use `assert "admin" in resp.text.lower()` instead of `resp.json()`

---

## Notes
This issue was identified during API automation testing (Round 2) and is related to BUG-AUTH-001. Both bugs affect admin endpoint behavior but are independent root causes.

---

# BUG-NOTIF-001 — Notification Flood from Non-Aggregated Module Open Events

## Summary
When multiple modules open simultaneously within a workshop cycle, the notification worker sends one email per module instead of aggregating them into a single notification.

---

## Severity
Medium (P2)

## Rationale
This issue does not break system functionality but creates a poor user experience by sending multiple redundant notifications for a single logical event (workshop cycle start). This increases the likelihood of notification fatigue and user opt-out.

---

## Impact
- Users receive multiple back-to-back emails for a single workshop event
- Reduces perceived quality of the notification system
- Increases risk of users disabling notifications entirely
- Misrepresents the underlying event structure (cycle start vs individual module opens)

---

## Environment
- Local development
- Notification worker (BullMQ)
- Email delivery via Postmark

---

## Preconditions
- Workshop with multiple modules
- Cycle start configured to open all modules simultaneously
- User with `module_open = true` and valid email channel

---

## Steps to Reproduce
1. Configure a workshop with multiple modules (e.g., 3–5 modules)
2. Ensure modules are scheduled to open at the same time
3. Start the workshop cycle (`POST /api/cycle/start/:workshopId`)
4. Observe notification worker logs and email inbox

---

## Expected Result
- A single email is sent per user for the workshop cycle start
- Email includes a list of all modules that have opened

---

## Actual Result
- One email is sent per module
- Users receive multiple emails in quick succession for the same workshop event

---

## Evidence
- Worker logs showing multiple notification jobs processed for the same cycle
- Email inbox showing multiple module open emails received

---

## Root Cause (Analysis)
The notification system treats each module open as an independent event rather than recognizing that all modules are opened as part of a single workshop cycle start.

---

## Recommendation
- Aggregate module open events into a single notification per workshop cycle
- Update notification worker logic to batch module events before dispatch
- Include all module names in a single email template

---

## Notes
This behavior is technically correct per current implementation but does not align with expected user-facing notification patterns for grouped events.

# BUG-NOTIF-002 — Incorrect Frontend URL in Notification Email Template

## Summary
Notification email template contains a hardcoded `localhost` URL, causing links to direct users to an invalid or inaccessible environment outside local development.

---

## Severity
Medium (P2)

## Rationale
This issue does not affect backend processing but directly impacts user navigation and usability in non-local environments. It would break core user flows in staging or production.

---

## Impact
- Users receive emails with incorrect links
- Navigation to workshop modules page fails outside local environment
- Breaks critical user journey from notification → application
- Reduces trust in notification system reliability

---

## Environment
- Local development (observed)
- Affects staging/production environments

---

## Preconditions
- User receives a module open notification email
- Email template includes link to workshop modules page

---

## Steps to Reproduce
1. Trigger a module open notification (e.g., start cycle)
2. Open received email
3. Click "Production Machinery" or module link

---

## Expected Result
- Link directs to correct frontend environment (e.g., production or configured base URL)

---

## Actual Result
- Link directs to:
  `http://localhost:5173/workshops/:id/modules`
- This is not accessible in non-local environments

---

## Evidence
- Email screenshot showing incorrect URL

---

## Root Cause (Analysis)
Frontend URL is hardcoded in the email template instead of being dynamically set via environment configuration.

---

## Recommendation
- Replace hardcoded URL with environment-based variable (e.g., `process.env.FRONTEND_URL`)
- Ensure correct base URL is used per environment (local, staging, production)

---

## Notes
This issue is acceptable in local testing but must be resolved before deployment to staging or production environments.
