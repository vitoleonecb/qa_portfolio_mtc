# Authentication Overview

## Feature Summary
The authentication feature manages user access, identity verification, and permission-based route protection across the application. It includes login, registration, logout, password reset, email confirmation, JWT-based session handling, and admin authorization.

## Key User Flows
- User registers and is logged in
- User logs in with email or username
- Authenticated user accesses protected routes with JWT
- User logs out and session is cleared
- User requests password reset and sets a new password
- User confirms email through tokenized confirmation flow
- Admin accesses admin-only routes

## Key Components
- Backend: auth routes, JWT issuance and verification, role checks, reset/confirmation token handling
- Frontend: login, registration, logout UI, protected page behavior, auth state updates
- Middleware: protected route enforcement, admin-only access checks
- Email flows: forgot password, reset password, confirmation, resend confirmation

## Critical Logic
- JWT must be issued with correct claims and expiry
- Protected routes must reject missing, invalid, expired, or tampered tokens
- Admin-only routes must enforce role authorization
- Auth state must update correctly after login, logout, and expired sessions
- Reset and confirmation tokens must only work for valid purpose and lifetime

## Risks / Complexity Areas
- Expired sessions may leave stale authenticated UI state
- Missing global auth cleanup can create UX/security gaps
- Token payload may expose unnecessary user data
- Password validation may be enforced inconsistently across flows
- Login may be allowed before email verification is complete
- Reset and confirmation flows depend on token correctness and email delivery

## Testing Focus
- Valid and invalid login behavior
- JWT issuance and token validation
- Protected route access control
- Admin vs non-admin authorization
- Registration and logout flows
- Forgot/reset password behavior
- Email confirmation and resend confirmation
- Logged-in vs logged-out UI state
