# TC-AUTH-014 — Auth State Not Invalidated After Token Expiration

## Severity
Critical

## Priority
P0

---

## Summary

Authenticated UI state is not cleared when a JWT expires and the backend returns a 401/403 response. The user remains in an invalid session state and can continue interacting with parts of the UI despite being unauthorized.

---

## Environment

- Frontend: React (Vite)
- Backend: Node.js / Express
- Auth: JWT-based authentication
- Browser: Safari (DevTools used)
- Execution Phase: Round 1 (Baseline)

---

## Preconditions

- User is logged in with a valid `accessToken`
- Token is allowed to expire (or manually replaced with expired token)

---

## Steps to Reproduce

1. Log in with valid credentials
2. Ensure `accessToken` is stored in `localStorage`
3. Allow token to expire (or manually inject expired token)
4. Navigate to a protected route (e.g., `/showcases`)
5. Trigger an API request requiring authentication

---

## Expected Result

- Backend returns 401/403 for expired token
- Frontend detects unauthorized response
- Auth state is cleared:
  - `localStorage.accessToken` removed
- User is redirected to `/login`
- UI updates to reflect logged-out state (no avatar, restricted access)

---

## Actual Result

- Backend returns 403 (observed in PM2 logs)
- UI continues to display authenticated state
- User is not redirected to login
- `accessToken` remains in `localStorage`
- Protected UI elements remain accessible until manual refresh or action

---

## Evidence

- Screenshot: `../../reports/TC-AUTH-014.png`
- PM2 logs show 403 response for protected route
- UI remains in authenticated state after failure

---

## Impact

- User operates in an invalid session state
- Potential security concern: UI does not reflect actual authorization state
- Confusing user experience (appears logged in but actions fail)
- Increased likelihood of inconsistent frontend/backend behavior

---

## Root Cause (Likely)

- No global interceptor or handler for 401/403 responses on the frontend
- Auth state is not centrally managed or invalidated on token failure

---

## Recommendation

Implement a global response interceptor (e.g., Axios or fetch wrapper) to:

- Detect 401/403 responses from protected endpoints
- Clear authentication state:
  - Remove `accessToken` from `localStorage`
- Redirect user to `/login`
- Optionally display a session-expired message

---

## Notes

- This issue was identified during Round 1 execution
- Re-tested in Round 2 after observability improvements to confirm backend rejection behavior
- UI behavior remains dependent on frontend handling and should be addressed independently of backend logging improvements
