### TC-NOTIF-001: Email sent when user channel is `email`

- **Feature / Requirement:** `notificationService.js:86–88` — email sent when channel is `email` or `both`
- **Priority:** P0
- **Preconditions:** User has `notification_settings.channel = "email"` and a valid `email` address.
- **Test Data:** Trigger any preference-gated notification (e.g., `moduleOpen`).
- **Steps:**
  1. Set user's notification channel to `email`.
  2. Trigger a moduleOpen notification for that user.
- **Expected Result:** Email is sent via Postmark. No SMS is sent.
- **Suggested Automation?** Yes (mock Postmark/Twilio in integration test)
- **Notes / Risk Covered:** Core routing logic. Verified at `notifyUser` level.

---

### TC-NOTIF-002: SMS sent when user channel is `sms`

- **Feature / Requirement:** `notificationService.js:90–92` — SMS sent when channel is `sms` or `both`
- **Priority:** P0
- **Preconditions:** User has `notification_settings.channel = "sms"` and a valid `user_phone`.
- **Test Data:** Trigger any preference-gated notification.
- **Steps:**
  1. Set user's notification channel to `sms`.
  2. Trigger a notification.
- **Expected Result:** SMS sent via Twilio. No email is sent.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** SMS-only delivery path.

---

### TC-NOTIF-003: Both email and SMS sent when channel is `both`

- **Feature / Requirement:** `notificationService.js:86–92` — both channels active
- **Priority:** P0
- **Preconditions:** User has `channel = "both"`, valid email, valid phone.
- **Test Data:** Trigger any preference-gated notification.
- **Steps:**
  1. Set channel to `both`.
  2. Trigger notification.
- **Expected Result:** Both Postmark email and Twilio SMS are sent concurrently (`Promise.allSettled`).
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Dual-delivery path.

---

### TC-NOTIF-004: No notification sent when channel is `none`

- **Feature / Requirement:** `notificationService.js:82` — early return on `none`
- **Priority:** P0
- **Preconditions:** User has `channel = "none"`.
- **Test Data:** Trigger any preference-gated notification.
- **Steps:**
  1. Set channel to `none`.
  2. Trigger notification.
- **Expected Result:** Neither email nor SMS is sent. Function returns immediately.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Opt-out enforcement.

---

### TC-NOTIF-005: SMS skipped when user_phone is empty/null

- **Feature / Requirement:** `notificationService.js:90` — `&& user.user_phone` check; `sendSms:43` — `if (!to) return`
- **Priority:** P1
- **Preconditions:** User has `channel = "both"` but `user_phone` is null or empty.
- **Test Data:** N/A.
- **Steps:**
  1. Set channel to `both`, leave phone blank.
  2. Trigger notification.
- **Expected Result:** Email is sent. SMS is silently skipped (no error).
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Graceful degradation when phone is missing.

---

### TC-NOTIF-006: Email failure does not block SMS (and vice versa)

- **Feature / Requirement:** `notificationService.js:94` — `Promise.allSettled` used for parallel dispatch
- **Priority:** P1
- **Preconditions:** Channel is `both`. One service is intentionally broken (e.g., invalid Postmark token).
- **Test Data:** N/A.
- **Steps:**
  1. Cause Postmark to reject (bad token).
  2. Trigger notification.
- **Expected Result:** Email fails and is logged. SMS still sends successfully. No unhandled exception.
- **Suggested Automation?** Yes (mock services)
- **Notes / Risk Covered:** `Promise.allSettled` ensures one failure doesn't abort the other.

---

### TC-NOTIF-007: parseSettings defaults to `{ channel: 'both' }` when settings are null

- **Feature / Requirement:** `notificationService.js:63`
- **Priority:** P2
- **Preconditions:** User has `notification_settings = NULL` in DB (e.g., pre-migration user).
- **Test Data:** User with null settings.
- **Steps:**
  1. Trigger a preference-gated notification for this user.
- **Expected Result:** `parseSettings` returns `{ channel: 'both' }`. User receives both email and SMS.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Backward compatibility for users created before the notification_settings column existed.

---
### TC-NOTIF-008: Confirm email — always sent regardless of preferences

- **Feature / Requirement:** `notificationWorker.js:410–422` — uses `sendEmail` directly, comment: "Always send, no preference check"
- **Priority:** P0
- **Preconditions:** User just registered.
- **Test Data:** New registration.
- **Steps:**
  1. Register a new user.
  2. Check that `confirmEmail` job is enqueued and processed.
- **Expected Result:**
  - Email sent to the registered address.
  - Subject: `[TEST] CONFIRM_EMAIL — MTC3`.
  - Body contains the user's name and a confirm URL with token.
  - Sent even if user's channel is `none`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Transactional emails must bypass preferences. Only email is sent (no SMS variant).

- **Actual Result:** User registers with no notifications enabled and still receives a confirmation email. Email contains user’s name and a confirm URL.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-NOTIF-009: Reset password — always sent regardless of preferences

- **Feature / Requirement:** `notificationWorker.js:427–438` — `sendEmail` directly, no preference check
- **Priority:** P0
- **Preconditions:** User triggered forgot-password.
- **Test Data:** Valid email.
- **Steps:**
  1. Call `POST /api/users/forgot-password` with a valid email.
  2. Observe `resetPassword` job processing.
- **Expected Result:** Email sent with reset URL. Subject: `[TEST] RESET_PASSWORD — MTC3`. Preferences ignored.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Security-critical transactional email.

- **Actual Result:** User with no notifications enabled and still receives a reset password email including a reset URL.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-NOTIF-010: Guest registration invite — always sent regardless of preferences

- **Feature / Requirement:** `notificationWorker.js:444–455` — `sendEmail` directly
- **Priority:** P1
- **Preconditions:** Guest user created via homepage flow.
- **Test Data:** Guest email submission.
- **Steps:**
  1. Submit responses as a guest on the homepage.
  2. Observe `guestRegistrationInvite` job.
- **Expected Result:** Email sent to guest's email. Contains registration URL with `?guest=<userId>&email=<email>`. No SMS.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Onboarding funnel — must always be delivered.

---
### TC-NOTIF-011: Module Open — sent to eligible users with `module_open = true`

- **Feature / Requirement:** `notificationWorker.js:124–147` — `getEligibleUsers('module_open')`
- **Priority:** P0
- **Preconditions:** Module transitions to `open` via worker. Users exist with `module_open = true` and `channel != 'none'`.
- **Test Data:** Workshop with module. Multiple users: one with `module_open = true`, one with `module_open = false`, one with `channel = 'none'`.
- **Steps:**
  1. Trigger `openModule` job → module becomes open → worker enqueues `moduleOpen`.
  2. Observe `moduleOpen` job processing.
- **Expected Result:**
  - User with `module_open = true`, `channel = 'email'` → email sent.
  - User with `module_open = false` → no notification.
  - User with `channel = 'none'` → no notification.
  - Email subject: `New Module Open — <workshopName>`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Broadcast notification with sub-option filtering. The `moduleOpen` template is the only one with a fully designed HTML layout (not a test scaffold).
- **Actual Result:**  
  Notification worker processed module open events and sent emails to users based on their notification preferences:
  - User with all notifications enabled received email notifications for each module opened.
  - User with all notifications disabled received no notifications.
  - User with notifications enabled but `module_open = false` received no notifications.

  Database values for `notification_settings` were respected correctly.  
  Email content included module information and a link to the workshop modules page.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-NOTIF-012: Last Day Reminder — filters out users who already completed all prompts

- **Feature / Requirement:** `notificationWorker.js:152–207` — per-user response count check
- **Priority:** P0
- **Preconditions:** Module is open, about to transition to processing. Users exist: one who completed all prompts, one who hasn't.
- **Test Data:** Module with 3 prompts. User A: 3 responses. User B: 1 response. Both have `last_day_reminder = true`.
- **Steps:**
  1. `lastDayReminder` job fires (~12s before processing).
  2. Observe which users receive notifications.
- **Expected Result:**
  - User A (completed) → NOT notified.
  - User B (incomplete) → notified.
  - Email includes deadline date from `cycle_jobs.scheduled_for`.
  - If no `cycle_jobs` row found, deadline shows `"soon"`.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Critical UX — don't nag users who already finished. The per-user query loop (line 183–193) is an N+1 pattern for large user bases.

---

### TC-NOTIF-013: Materials Ready — respects `materials_ready` sub-option

- **Feature / Requirement:** `notificationWorker.js:212–237` — per-user settings check
- **Priority:** P1
- **Preconditions:** All modules completed. Worker sends `materialsReady` with eligible user IDs.
- **Test Data:** 2 eligible users: one with `materials_ready = true`, one with `materials_ready = false`.
- **Steps:**
  1. All modules complete → worker enqueues `materialsReady`.
  2. Observe notification delivery.
- **Expected Result:** Only user with `materials_ready = true` receives notification.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Sub-option gating in the worker (not via `getEligibleUsers` — uses manual check loop).

---

### TC-NOTIF-014: Workshop RSVP Unconfirmed — respects `workshop_rsvp` sub-option

- **Feature / Requirement:** `notificationWorker.js:242–263` — checks `settings.workshop_rsvp`
- **Priority:** P0
- **Preconditions:** RSVP created for a user (via module completion or manual creation).
- **Test Data:** User with `workshop_rsvp = true`, user with `workshop_rsvp = false`.
- **Steps:**
  1. RSVP created → `workshopRsvpUnconfirmed` enqueued.
  2. Worker processes job.
- **Expected Result:** User with `workshop_rsvp = true` receives email. User with `workshop_rsvp = false` does not.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Targeted single-user notification.

- **Actual Result:**  
  RSVP records were created for both users and `workshopRsvpUnconfirmed` jobs were enqueued for each.  
  Notification worker ultimately sent the email only for the user whose `notification_settings.workshop_rsvp = true`.  
  No email was sent for the user whose `workshop_rsvp = false`, which matches expected preference-gated behavior.

- **Status:** Pass

- **Evidence:** Screenshot available in `../../reports`

---

### TC-NOTIF-015: Showcase Ticket — respects `showcase_ticket` sub-option

- **Feature / Requirement:** `notificationWorker.js:344–368`
- **Priority:** P1
- **Preconditions:** Stripe webhook fires `payment_intent.succeeded` with `metadata.type = 'showcase_ticket'`.
- **Test Data:** User with `showcase_ticket = true`.
- **Steps:**
  1. Simulate successful Stripe payment.
  2. `showcaseTicket` job enqueued and processed.
- **Expected Result:** User receives email/SMS confirming their ticket. Subject includes showcase name and date.
- **Suggested Automation?** Partial (requires Stripe webhook mock)
- **Notes / Risk Covered:** Payment confirmation notification.

---

### TC-NOTIF-016: New Showcase — sent only to non-subscribers with `showcase_announcements = true`

- **Feature / Requirement:** `notificationWorker.js:373–405` — explicit `NOT IN (active subscribers)` query
- **Priority:** P1
- **Preconditions:** Admin creates a new showcase. Mix of subscribers and non-subscribers.
- **Test Data:** 3 users: subscriber with `showcase_announcements = true`, non-subscriber with `showcase_announcements = true`, non-subscriber with `showcase_announcements = false`.
- **Steps:**
  1. Admin creates showcase via `POST /api/showcases`.
  2. `newShowcase` job processes.
- **Expected Result:**
  - Subscriber → NOT notified (they get tickets via `showcaseRsvpUnconfirmed` path).
  - Non-subscriber with `showcase_announcements = true` → notified.
  - Non-subscriber with `showcase_announcements = false` → NOT notified.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Audience segmentation — subscribers and non-subscribers get different notification types for the same event.

---

### TC-NOTIF-017: Showcase RSVP Unconfirmed — sent to subscribers, respects `showcase_announcements`

- **Feature / Requirement:** `notificationWorker.js:313–338`
- **Priority:** P1
- **Preconditions:** Monthly showcase check or batch-ticket creation runs. Subscribers get unconfirmed tickets.
- **Test Data:** 2 subscribers: one with `showcase_announcements = true`, one with `showcase_announcements = false`.
- **Steps:**
  1. `showcaseRsvpUnconfirmed` job fires with user IDs.
  2. Worker processes each user.
- **Expected Result:** Only subscriber with `showcase_announcements = true` is notified.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Sub-option gating for showcase-related notifications.

---
