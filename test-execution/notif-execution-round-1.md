# Notifications Test Execution — Round 1

## Overview

This document summarizes the first round of manual execution for the notifications feature.

Round 1 was intentionally limited to the highest-risk and most portfolio-relevant notification scenarios, with emphasis on:

- Transactional email behavior
- Preference-gated delivery
- Notification settings API validation
- Notification settings persistence
- Settings page behavior
- Authorization/security on settings update

---

## Execution Summary

- Total Test Cases Planned: 12  
- Executed: 12  
- Passed: 11 
- Failed: 1 
- Inconclusive: 0  
- Blocked: 0 

- Execution Rate: 100%
- Pass Rate: 91.7%
---

## Test Cases Executed

| Test ID | Title | Status | Notes |
|---|---|---|---|
| TC-NOTIF-008 | Confirm email always sent regardless of preferences | Pass | |
| TC-NOTIF-009 | Reset password always sent regardless of preferences | Pass | |
| TC-NOTIF-011 | Module Open sent to eligible users with `module_open = true` | Pass | Notification Flood from Non-Aggregated Module Open Events |
| TC-NOTIF-014 | Workshop RSVP Unconfirmed respects `workshop_rsvp` sub-option | Pass | RSVP notification jobs were enqueued for both users before preference filtering |
| TC-NOTIF-022 | GET notification settings returns stored preferences | Pass | |
| TC-NOTIF-024 | PUT notification settings accepts valid payload | Pass | |
| TC-NOTIF-025 | PUT notification settings rejects invalid channel | Pass | |
| TC-NOTIF-026 | PUT notification settings rejects non-boolean sub-options | Pass | |
| TC-NOTIF-027 | PUT notification settings does not validate user owns the ID | Fail | Security-focused case |
| TC-NOTIF-030 | Registration notification settings are saved with the user record | Pass | |
| TC-NOTIF-031 | Settings page loads saved notification preferences on mount | Pass | |
| TC-NOTIF-032 | Settings page master toggle disables all notifications | Pass | |

---

## Scope Covered

### Functional areas covered in Round 1
- Transactional notifications
- Preference-gated notifications
- Notification settings API
- Validation of settings payloads
- Notification settings persistence
- Settings page behavior
- Authorization/security on settings updates

---

## Notable Observations

### Bugs and Risks Identified
- **TC-NOTIF-011 — Notification Flood from Non-Aggregated Module Open Events:**  
  When multiple modules open simultaneously within a workshop cycle, the notification worker sends one email per module instead of aggregating them into a single notification.

  **Impact:** Users may receive multiple back-to-back emails for a single workshop event, increasing likelihood of notification fatigue, disengagement, or opt-out. This behavior does not align with expected batching of related events.  
  **Severity:** Medium (P2 — user experience / notification system design flaw)  
  **Status:** Promoted to bug report — aggregation expected for simultaneous lifecycle events  
  **Recommendation:** Aggregate module open notifications into a single email per workshop cycle. Include all opened modules in the email body instead of sending separate emails.

- **TC-NOTIF-011 — Incorrect Frontend URL in Email Template:**  
  Email template contains a hardcoded frontend URL using `localhost` instead of the correct environment-based URL. Link directs users to `http://localhost:5173/...` instead of the expected application host.

  **Impact:** Users in non-local environments (e.g., staging/production) will receive broken or inaccessible links in notification emails.  
  **Severity:** Medium (P2 — broken navigation / environment misconfiguration)  
  **Status:** Promoted to bug report — environment-specific but critical for production readiness  
  **Recommendation:** Replace hardcoded URL with environment-based configuration (e.g., `process.env.FRONTEND_URL`) to ensure correct routing across environments.

- **TC-NOTIF-027 — Missing Authorization Check on Notification Settings Endpoint (IDOR):**  
  The `PUT /api/users/:id/notification-settings` endpoint allows any authenticated user to modify another user's notification settings. The endpoint validates authentication but does not verify ownership (`req.user.user_id === id`).

  **Impact:** Unauthorized users can modify notification preferences for any account, leading to privacy violations and potential abuse (e.g., disabling notifications or altering delivery channels).  
  **Severity:** High (P1 — security / IDOR vulnerability)  
  **Status:** Promoted to bug report — confirmed via API testing  
  **Recommendation:** Enforce ownership validation by ensuring the authenticated user's ID matches the target ID, or restrict access to admins only where appropriate.

---

## Evidence
- `../reports/TC-NOTIF-008.png`
- `../reports/TC-NOTIF-009.png`
- `../reports/TC-NOTIF-011-server-logs-email.png`
- `../reports/TC-NOTIF-011-user-settings.png`
- `../reports/TC-NOTIF-014.png`
- `../reports/TC-NOTIF-022.png`
- `../reports/TC-NOTIF-024.png`
- `../reports/TC-NOTIF-025.png`
- `../reports/TC-NOTIF-026.png`
- `../reports/TC-NOTIF-027.png`
- `../reports/TC-NOTIF-030.png`
- `../reports/TC-NOTIF-031.png`
- `../reports/TC-NOTIF-032.png`

---

## Key Findings

### 1. Critical Security Gap Identified
- The notification settings API contains an **IDOR vulnerability** allowing users to modify other users’ preferences.
- This represents a **high-risk access control failure** and was the only failing test in this round.

### 2. Notification System Behavior Is Functionally Correct but Not Optimized
- Preference-based delivery logic is working correctly:
  - Users only receive notifications aligned with their saved settings
  - Transactional emails correctly bypass preferences
- However, the system processes notifications at a **per-event level rather than aggregating related events**, leading to redundant emails.

### 3. Event Modeling Misalignment in Notification Flow
- Workshop module openings are treated as independent events instead of a single cycle-level event.
- This results in multiple notifications for what is logically a single user-facing action (workshop cycle start).

### 4. Minor Efficiency Consideration in Worker Processing
- Notification jobs are enqueued for all users before preference filtering occurs.
- While delivery is correctly suppressed, this may introduce unnecessary processing overhead at scale.

### 5. Environment Configuration Risk in Email Templates
- Email templates rely on hardcoded frontend URLs (`localhost`), which would break navigation in non-local environments.
- Indicates missing environment-based configuration for external links.

### 6. Strong Coverage of Core Notification System Behavior
- Successfully validated:
  - Transactional vs preference-gated notifications
  - Notification settings API validation
  - Settings persistence and UI synchronization
  - Worker-based notification delivery
- Demonstrates end-to-end reliability across API, worker, and UI layers (excluding identified issues)
