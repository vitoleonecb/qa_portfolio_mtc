### TC-NOTIF-018: Monthly showcase check — sends tickets on the 1st if an upcoming showcase exists

- **Feature / Requirement:** `notificationWorker.js:268–308` — repeatable cron `'0 14 1 * *'`
- **Priority:** P1
- **Preconditions:** An upcoming showcase exists. No monthly record for this month.
- **Test Data:** Showcase with `showcase_status = 'upcoming'` and `showcase_date >= NOW()`.
- **Steps:**
  1. `monthlyShowcaseCheck` fires (cron or manual trigger).
  2. Observe batch-ticket creation and notification dispatch.
- **Expected Result:**
  - Membership tickets created for eligible subscribers.
  - `showcaseRsvpUnconfirmed` job enqueued.
  - `monthly_showcase_notifications` row inserted with `status = 'sent'`.
- **Suggested Automation?** Yes (trigger job manually in test)
- **Notes / Risk Covered:** Monthly lifecycle for subscriber tickets.

---

### TC-NOTIF-019: Monthly showcase check — idempotent on re-run

- **Feature / Requirement:** `notificationWorker.js:276–278` — checks `status === 'sent'` and breaks
- **Priority:** P2
- **Preconditions:** `monthly_showcase_notifications` row exists for this month with `status = 'sent'`.
- **Test Data:** N/A.
- **Steps:**
  1. Trigger `monthlyShowcaseCheck` again for the same month.
- **Expected Result:** Worker logs "Monthly showcase already sent" and skips. No duplicate tickets or notifications.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Idempotency guard for repeatable cron jobs.

---

### TC-NOTIF-020: Monthly showcase check — marks pending when no showcase exists

- **Feature / Requirement:** `notificationWorker.js:298–306`
- **Priority:** P2
- **Preconditions:** No upcoming showcase in DB.
- **Test Data:** N/A.
- **Steps:**
  1. `monthlyShowcaseCheck` fires.
- **Expected Result:** `monthly_showcase_notifications` row inserted with `status = 'pending'`. No tickets or notifications.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Deferred processing — the `showcaseCreatedFallback` handler picks this up later.

---

### TC-NOTIF-021: Showcase created fallback — processes pending monthly row

- **Feature / Requirement:** `notificationWorker.js:461–482`
- **Priority:** P2
- **Preconditions:** `monthly_showcase_notifications` row exists with `status = 'pending'` for current month.
- **Test Data:** Admin creates a showcase after the 1st of the month.
- **Steps:**
  1. Admin creates showcase → `showcaseCreatedFallback` enqueued.
  2. Worker finds pending row, runs `processShowcaseBatchTickets`.
- **Expected Result:** Tickets created for subscribers. Row updated to `status = 'sent'`. Notifications dispatched.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Late-showcase scenario where showcase is created after the monthly cron already ran.

---
### TC-NOTIF-035: Module Open email template contains correct dynamic data

- **Feature / Requirement:** `templates/emails/moduleOpen.js` — fully designed HTML template
- **Priority:** P1
- **Preconditions:** Module opening triggers notification.
- **Test Data:** Workshop "Jazz Workshop", Module "Week 1".
- **Steps:**
  1. Trigger `moduleOpen` notification.
  2. Inspect the sent email HTML.
- **Expected Result:**
  - Subject: `New Module Open — Jazz Workshop`.
  - Body contains workshop name in italics, module name in bold.
  - CTA button links to correct workshop modules URL.
  - Footer contains account/contact/unsubscribe links.
- **Suggested Automation?** Yes (template unit test)
- **Notes / Risk Covered:** Only `moduleOpen` has a production-quality template. All others use `[TEST]` scaffold subjects.

---

### TC-NOTIF-036: SMS body contains correct data and app URL

- **Feature / Requirement:** Various SMS strings in `notificationWorker.js` (e.g., line 144, 204, 260)
- **Priority:** P1
- **Preconditions:** User with `channel = 'sms'`.
- **Test Data:** Trigger each notification type.
- **Steps:**
  1. For each notification type, verify the SMS body string.
- **Expected Result:** Each SMS includes: `MTC3 —` prefix, relevant names/dates, and a clickable URL. SMS is a single string (no HTML).
- **Suggested Automation?** Yes (unit tests for SMS string generation)
- **Notes / Risk Covered:** SMS has character limits (~160 for standard). Some SMS bodies may exceed this. No truncation logic exists.

---
### TC-NOTIF-037: Worker handles missing module/workshop gracefully

- **Feature / Requirement:** `notificationWorker.js:132` — `if (!mod || !ws) break`
- **Priority:** P2
- **Preconditions:** `moduleOpen` job enqueued with an invalid `moduleId`.
- **Test Data:** `{ moduleId: 99999, workshopId: 1 }`
- **Steps:**
  1. Enqueue `moduleOpen` job with non-existent module.
- **Expected Result:** Worker breaks out of the case. No notification sent. No crash.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Same pattern exists for most notification types — they all break on missing DB rows.

---

### TC-NOTIF-038: Worker handles unknown job name

- **Feature / Requirement:** `notificationWorker.js:484–485` — default case
- **Priority:** P2
- **Preconditions:** Job with name `"foobar"` enqueued to `notificationQueue`.
- **Test Data:** N/A.
- **Steps:**
  1. Enqueue unknown job.
- **Expected Result:** Worker logs `[notificationWorker] Unknown job: foobar`. No crash.
- **Suggested Automation?** Yes
- **Notes / Risk Covered:** Unlike the module worker, this default case is safe — no subsequent DB operations.

---
