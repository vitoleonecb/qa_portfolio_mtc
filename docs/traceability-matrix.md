## Authentication Coverage

| Feature Area | Requirement Description | Test Cases | Execution Reference | Bugs / Risks | Automation Coverage |
|-------------|--------------------------|------------|--------------------|--------------|---------------------|
| Login (Valid) | User can log in with valid credentials by email or username | TC-AUTH-001, TC-AUTH-002 | auth-execution-round-1.md | — | Yes — high value for UI + API regression |
| Login (Invalid) | System rejects incorrect credentials | TC-AUTH-005, TC-AUTH-006 | auth-execution-round-1.md | Potential brute-force risk due to no rate limiting | Yes — strong API automation candidate |
| Login Validation | Prevent empty or missing required inputs | TC-AUTH-007, TC-AUTH-008, TC-AUTH-009 | auth-execution-round-1.md | — | Yes — UI validation is stable and repeatable |
| Error Handling | System handles backend/API failure gracefully | TC-AUTH-011 | Partial | Generic error messaging may hide root cause | Partial — worth automating only if failures can be mocked cleanly |
| JWT Issuance | Token is generated with correct claims and expiry | TC-AUTH-003 | auth-execution-round-1.md | Token contains PII in payload | Yes — best as API automation |
| Session Handling | Token is stored, cleared, and used correctly across auth flows | TC-AUTH-001, TC-AUTH-030 | auth-execution-round-1.md | No refresh token mechanism | Yes — important UI regression coverage |
| Protected Routes | Requests without valid auth are rejected | TC-AUTH-012, TC-AUTH-013, TC-AUTH-014 | auth-execution-round-1.md / auth-execution-round-2.md | UX gap when expired sessions occur | Yes — excellent API automation candidate |
| Role Authorization | Admin routes allow admins and reject non-admins | TC-AUTH-016, TC-AUTH-017 | auth-execution-round-1.md | UI may rely on stale token claims | Yes — high-value API automation |
| Token Integrity | Tampered or invalid tokens are rejected | TC-AUTH-013 | auth-execution-round-1.md | — | Yes — fast API test |
| Token Expiry | Expired tokens are rejected correctly | TC-AUTH-014 | auth-execution-round-1.md | No automatic logout handling | Yes — API automation preferred |
| Deleted User Handling | Tokens for removed users no longer work | TC-AUTH-015 | Not Executed | — | Yes — good API automation if seed/reset data is manageable |
| Registration | User can successfully register and auto-log in | TC-AUTH-033 | auth-execution-round-1.md | Email verification not enforced at login | Yes — strong end-to-end UI flow |
| Logout | User session is cleared and login screen is shown | TC-AUTH-030 | auth-execution-round-1.md | — | Yes — very worth automating |
| Forgot Password | Password recovery can start without user enumeration | TC-AUTH-019, TC-AUTH-020 | auth-execution-round-1.md / auth-execution-round-2.md  | — | Partial — API yes, email delivery itself may be harder |
| Reset Password | User can set a new password with a valid reset token | TC-AUTH-022 | auth-execution-round-1.md / auth-execution-round-2.md  | Observability improvements added to server side logging | Yes — very good API and UI candidate |
| Reset Token Validation | Invalid, expired, or wrong-purpose tokens are rejected | TC-AUTH-023, TC-AUTH-024 / auth-execution-round-2.md  | auth-execution-round-1.md | — | Yes — strong API automation |
| Password Validation | Password rules are enforced during reset flow | TC-AUTH-026 | auth-execution-round-1.md | Backend does not enforce complexity consistently | Yes — UI validation automation is worthwhile |
| Email Confirmation | User can confirm email with a valid token | TC-AUTH-027 | auth-execution-round-1.md | Login allowed without verification | Partial — automate if confirmation token generation is accessible |
| Resend Confirmation | User can request a new confirmation email | TC-AUTH-029 | Not Executed | — | Partial — API worth automating, delivery less important |
| UI Auth State | UI updates correctly for logged-in vs logged-out users | TC-AUTH-031, TC-AUTH-032 | auth-execution-round-1.md | Missing global route guards | Yes — very good Playwright candidate |

## Authentication Coverage Summary

- Total Test Cases: 37
- Executed: 31
- Execution Rate: 83.8%
- High-priority automation targets:
  - Login / logout
  - Registration
  - Protected route access
  - Admin authorization
  - Reset password
  - JWT validation
- Best manual-only or partial-manual areas:
  - Email delivery confirmation
  - Infrastructure-failure UX
  - Exploratory auth edge cases

## Modules Coverage

> Note: Modules testing focuses on lifecycle-driven behavior, where UI, backend state, and scheduled transitions are tightly coupled.

| Feature Area | Requirement Description | Test Cases | Execution Reference | Bugs / Risks | Automation Coverage |
|-------------|--------------------------|------------|--------------------|--------------|---------------------|
| Module Creation | Admin can create modules via UI and API | TC-MOD-001 | mod-execution-round1.md | No backend validation on module name | Yes — API + UI |
| Authorization | Non-admin users cannot create modules | TC-MOD-003 | mod-execution-round1.md | — | Yes — API |
| Status Management | Admin can manually update module status | TC-MOD-007 | mod-execution-round1.md | No enum validation on status | Yes — API |
| Scheduler Validation | Modules cannot start without prompts | TC-MOD-010 | mod-execution-round1.md | — | Yes — API |
| Module List UI | Modules are grouped correctly by status | TC-MOD-015 | mod-execution-round1.md | UI depends on backend status accuracy | Yes — UI |
| Progress Tracking | Progress reflects responses vs prompts | TC-MOD-016 | mod-execution-round1.md | Progress disappears when not "open", which is fine for current implementation | Yes — UI |
| Response Submission | User can submit prompt responses successfully | TC-MOD-022 | mod-execution-round1.md | No duplicate-response guard | Yes — API + UI |
| End-of-Module Flow | System determines next step after final prompt | TC-MOD-024 | mod-execution-round1.md | Logic tightly coupled to progress data | Partial — E2E |
| RSVP Completion | RSVP is earned after all modules complete | TC-MOD-026, TC-MOD-028 | mod-execution-round1.md | Dual RSVP creation paths | Partial — E2E |
| RSVP State UI | Detail card reflects locked vs ready state | TC-MOD-029 | mod-execution-round1.md | — | Yes — UI |
| Prompt Editor | Admin can submit prompts for a module | TC-MOD-032 | mod-execution-round1.md | Misleading success message | Yes — UI |

## Module Coverage Summary

- Total Test Cases (full suite): 33
- Executed (Round 1): 12
- Execution Rate: 36.4%
- High-priority automation targets:
  - Module creation and deletion (API)
  - Authorization enforcement (admin vs. non-admin)
  - Status transition validation (API)
  - Response submission (API + UI)
- Best manual-only or partial-manual areas:
  - End-of-module flow (requires full E2E state setup)
  - RSVP completion path (multiple code paths)
  - Scheduler timing behavior
- Focus: High-risk workflow validation (state transitions, completion logic, RSVP flow)

## Notifications Coverage

| Feature Area | Requirement Description | Test Cases | Execution Reference | Bugs / Risks | Automation Coverage |
|-------------|--------------------------|------------|---------------------|--------------|---------------------|
| Channel Routing | Notification service respects channel preference (`email`, `sms`, `both`, `none`) | TC-NOTIF-001, TC-NOTIF-002, TC-NOTIF-003, TC-NOTIF-004 | notif-execution-round-1.md | Three different default channel values across DB, registration, and settings page | Yes — strong service/integration automation candidate |
| Delivery Fallback | Missing phone or one-channel failure does not block other valid delivery path | TC-NOTIF-005, TC-NOTIF-006, TC-NOTIF-007 | Not Executed | Missing phone silently downgrades `both` to email-only; no explicit retry config | Yes — best with mocked Postmark/Twilio |
| Transactional Email | Confirm email, reset password, and guest registration invite are always sent regardless of preferences | TC-NOTIF-008, TC-NOTIF-009, TC-NOTIF-010 | notif-execution-round-1.md | Most transactional templates still use `[TEST]` subject prefixes | Yes — high-value integration/API automation |
| Preference-Gated Delivery | Module/workshop/showcase notifications respect saved sub-option preferences | TC-NOTIF-011, TC-NOTIF-012, TC-NOTIF-013, TC-NOTIF-014, TC-NOTIF-015, TC-NOTIF-016, TC-NOTIF-017 | notif-execution-round-1.md | `showcaseRsvpUnconfirmed` shares `showcase_announcements` toggle; users cannot separate RSVP vs promo preferences | Yes — strong worker/integration automation |
| Monthly Showcase Check | Monthly cron sends, skips, or defers showcase notifications correctly | TC-NOTIF-018, TC-NOTIF-019, TC-NOTIF-020, TC-NOTIF-021 | Not Executed | Idempotency and fallback logic depend on monthly tracking row state | Partial — best as worker/job integration tests |
| Settings API (Read) | API returns stored notification settings for a valid user | TC-NOTIF-022, TC-NOTIF-023 | notif-execution-round-1.md | — | Yes — fast API automation |
| Settings API (Write) | API accepts valid settings and rejects invalid channel or invalid boolean payloads | TC-NOTIF-024, TC-NOTIF-025, TC-NOTIF-026 | notif-execution-round-1.md | Input validation depends on API layer only | Yes — excellent API automation candidate |
| Settings Authorization | Authenticated users should not be able to update another user’s notification settings | TC-NOTIF-027 | notif-execution-round-1.md | IDOR vulnerability — endpoint does not verify ownership | Yes — high-priority API security automation |
| Registration Preferences | Registration page applies defaults, validates phone conditionally, and persists settings with new user | TC-NOTIF-028, TC-NOTIF-029, TC-NOTIF-030 | notif-execution-round-1.md | Registration defaults differ from DB and profile settings defaults | Yes — strong end-to-end UI candidate |
| Settings Page State | Profile settings page loads, updates, and persists notification preferences immediately | TC-NOTIF-031, TC-NOTIF-032, TC-NOTIF-033, TC-NOTIF-034 | notif-execution-round-1.md | Settings page fallback default may hide toggles if fetch fails | Yes — very good Playwright candidate |
| Template Content | Email and SMS templates contain correct dynamic data and usable links/content | TC-NOTIF-035, TC-NOTIF-036 | Not Executed | SMS length not validated; most email templates still look like test scaffolds | Partial — template/unit automation is ideal |
| Worker Error Handling | Worker handles missing DB rows and unknown job names gracefully | TC-NOTIF-037, TC-NOTIF-038 | Not Executed | No explicit retry/dead-letter strategy on queue failures | Yes — targeted worker automation |

## Notifications Coverage Summary

- Total Test Cases: 38
- Executed: 12
- Execution Rate: 31.6%
- High-priority automation targets:
  - Notification settings API
  - Settings authorization / IDOR check
  - Transactional email dispatch
  - Preference-gated notification routing
  - Settings page persistence
- Best manual-only or partial-manual areas:
  - Monthly showcase cron behavior
  - Template rendering/content review
  - External provider failure behavior
---

## Recommended Automation Strategy

### Best UI Automation Candidates
These are worth covering in Playwright because they represent visible user value and stable regression paths:
- Valid login
- Invalid login
- Empty-field validation
- Registration → auto-login
- Logout
- Reset password UI
- Logged-in / logged-out header state
- Redirect behavior for unauthenticated users

### Best API Automation Candidates
These give strong security and logic coverage quickly:
- Invalid credentials
- Missing token
- Invalid token
- Expired token
- Admin vs non-admin route access
- JWT payload validation
- Reset token validation
- Non-enumerating forgot-password behavior

### Partial / Lower-Value Automation
These are useful, but only after the core suite is in place:
- Server-down login behavior
- Email confirmation delivery
- Resend confirmation delivery
- Deleted-user token scenario if setup is cumbersome
