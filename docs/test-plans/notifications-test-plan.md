# Notifications Test Plan

## Related Artifacts
- Test Cases: [`test-cases/notifications/`](../../test-cases/notifications/)
- Execution Reports:
  - [`notif-execution-round-1.md`](../../test-execution/notif-execution-round-1.md)
- Bug Reports: [`bug-reports/`](../../bug-reports/)
- Templates: [`test-case-template.md`](../../templates/test-case-template.md)

---

## 1. Test Plan ID
TP-NOTIF-001

## 2. Overview
This test plan covers the notification system, including transactional email delivery, preference-gated notifications, notification settings management, and BullMQ worker behavior.

The goal is to verify that notifications are routed correctly based on user preferences, that transactional emails bypass preferences, that the settings API enforces proper validation and authorization, and that the worker handles various job types reliably.

---

## 3. Feature Overview
The notifications feature manages communication across email (Postmark) and SMS (Twilio) channels. It includes:
- Transactional notifications (confirm email, reset password, guest invite) that always send regardless of preferences
- Preference-gated notifications (module open, last day reminder, materials ready, workshop RSVP, showcase announcements, showcase tickets) that respect user-configured channel and sub-option settings
- A notification settings API for reading and updating preferences
- A BullMQ worker that processes notification jobs from a queue
- Frontend settings management on the registration page and profile settings page

---

## 4. Objectives
- Verify transactional notifications are always sent regardless of user preferences
- Verify preference-gated notifications respect channel (`email`, `sms`, `both`, `none`) and sub-option settings
- Validate the notification settings API enforces input validation
- Confirm the settings API enforces authorization (users can only modify their own settings)
- Verify the settings page correctly loads, displays, and persists notification preferences
- Verify registration defaults are applied and persisted correctly
- Validate worker error handling for missing data and unknown job types

---

## 5. Scope

### In Scope
- Channel routing (`email`, `sms`, `both`, `none`)
- Transactional email delivery (confirm email, reset password, guest invite)
- Preference-gated delivery for module, workshop, and showcase notifications
- Notification settings API (GET and PUT)
- Input validation on settings payloads
- Authorization enforcement on settings endpoint
- Registration notification defaults and persistence
- Settings page behavior (load, toggle, channel cycle, persistence)
- Worker error handling

Associated test case files:
- `test-cases/notifications/notifications-delivery.md`
- `test-cases/notifications/notification-settings.md`
- `test-cases/notifications/notification-content-and-worker-behavior.md`
- `test-cases/notifications/notifications-overview.md`

### Out of Scope
- Full external email/SMS delivery verification (Postmark/Twilio infrastructure)
- Performance or load testing of the notification worker
- Monthly showcase cron timing accuracy
- SMS character length validation
- Template rendering/visual QA beyond content correctness

---

## 6. Test Approach

### Manual Testing
Manual testing will be used to verify:
- End-to-end notification delivery flows
- Settings page UI behavior
- Registration notification defaults
- Worker log inspection for job processing
- Authorization boundary testing via API

### Automated Testing
Automation will be used for:
- Notification settings API validation (valid/invalid payloads)
- Authorization enforcement (IDOR check)
- Settings persistence verification
- Transactional email dispatch confirmation

### Risk-Based Prioritization
Priority is given to:
1. Authorization enforcement (IDOR vulnerability)
2. Transactional email delivery (security-critical)
3. Preference-gated routing correctness
4. Settings API input validation
5. Settings page persistence and UI behavior
6. Worker error handling

---

## 7. Test Types
- Functional Testing
- Negative Testing
- Validation Testing
- Authorization / Security Testing
- Integration Testing (worker + API + DB)
- UI / UX Testing

---

## 8. Round 1 Planned Coverage

The following test cases are planned for Round 1 execution:

- TC-NOTIF-008 — Confirm email always sent regardless of preferences
- TC-NOTIF-009 — Reset password always sent regardless of preferences
- TC-NOTIF-011 — Module Open sent to eligible users with `module_open = true`
- TC-NOTIF-014 — Workshop RSVP Unconfirmed respects `workshop_rsvp` sub-option
- TC-NOTIF-022 — GET notification settings returns stored preferences
- TC-NOTIF-024 — PUT notification settings accepts valid payload
- TC-NOTIF-025 — PUT notification settings rejects invalid channel
- TC-NOTIF-026 — PUT notification settings rejects non-boolean sub-options
- TC-NOTIF-027 — PUT notification settings does not validate user owns the ID (security)
- TC-NOTIF-030 — Registration notification settings are saved with the user record
- TC-NOTIF-031 — Settings page loads saved notification preferences on mount
- TC-NOTIF-032 — Settings page master toggle disables all notifications

---

## 9. Entry Criteria
Testing will begin when:
- Application is running locally with backend, frontend, Redis, and BullMQ worker
- Test user accounts are available with configurable notification settings
- Notification worker is processing jobs
- Postmark and Twilio integrations are configured (or test/sandbox mode is active)
- Tester has access to worker logs, database, and API inspection tools

---

## 10. Exit Criteria
This test plan is complete for Round 1 when:
- All selected Round 1 test cases have been executed
- Each test case has a recorded status with evidence
- Security issues are documented as bug reports
- Execution results are summarized in the Round 1 execution file

---

## 11. Test Environment
- Environment: Local development
- Frontend: React (Vite) on `localhost:5173`
- Backend: Node.js / Express on `localhost:3036`
- Database: MySQL
- Queue: Redis + BullMQ
- Email: Postmark (test/sandbox mode)
- SMS: Twilio (test/sandbox mode)
- Primary Browser: Chrome
- Supporting Tools: Browser DevTools, curl, PM2 logs, Playwright (Python), Python `requests`, screenshots

---

## 12. Test Data
The following test data is required:
- User with `channel = 'email'` and all sub-options enabled
- User with `channel = 'none'` (opted out)
- User with mixed sub-option states (some enabled, some disabled)
- Two distinct user accounts for IDOR authorization testing
- Fresh registration data for defaults testing
- Workshop with modules for triggering notification events

---

## 13. Roles and Responsibilities

| Role | Responsibility |
|------|----------------|
| QA Engineer | Design test cases, execute tests, document issues, summarize risks |
| Developer | Clarify intended behavior, investigate issues, implement fixes |

---

## 14. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| IDOR on notification settings endpoint | Any user can modify another user's preferences | Test cross-user update via API, document as security bug |
| Mismatched defaults across DB, registration, and settings page | Users may have unexpected notification states | Verify defaults at each entry point, document inconsistencies |
| Notification flood from non-aggregated module open events | Poor user experience, notification fatigue | Test multi-module open scenario, document aggregation gap |
| Hardcoded localhost URLs in email templates | Broken links in non-local environments | Inspect email content, document as environment config bug |
| Worker processes jobs for all users before preference filtering | Unnecessary processing overhead at scale | Document as optimization opportunity |
| Missing retry/dead-letter strategy on queue failures | Silent notification loss | Test worker error handling, document gap |

---

## 15. Traceability

| Feature Area | Test Cases | Execution | Bugs |
|-------------|-----------|----------|------|
| Channel Routing | test-cases/notifications/notifications-delivery.md | notif-execution-round-1.md | — |
| Transactional Email | test-cases/notifications/notifications-delivery.md | notif-execution-round-1.md | — |
| Preference-Gated Delivery | test-cases/notifications/notifications-delivery.md | notif-execution-round-1.md | bug-reports/minor.md |
| Settings API | test-cases/notifications/notification-settings.md | notif-execution-round-1.md | bug-reports/major.md |
| Settings UI | test-cases/notifications/notification-settings.md | notif-execution-round-1.md | — |
| Worker Behavior | test-cases/notifications/notification-content-and-worker-behavior.md | Not Executed | — |

---

## 16. Assumptions
- Postmark and Twilio are configured in test/sandbox mode for safe testing
- Notification settings can be modified directly via API or database for test setup
- BullMQ worker is running and processing jobs during test execution
- Transactional notifications are expected to always send regardless of user preferences

---

## 17. Constraints
- Full external delivery verification depends on Postmark/Twilio sandbox behavior
- Monthly cron job timing cannot be easily tested in a local environment
- Some notification types require specific application state (e.g., RSVP creation, showcase existence)
- Worker behavior testing requires Redis and BullMQ to be running

---

## 18. Approval
| Name | Role |
|------|------|
| Corey Brewer | QA Engineer |

---

## 19. Deliverables
- Notification test case files in `test-cases/notifications/`
- Notification execution report for Round 1
- Bug reports for reproduced defects (including IDOR vulnerability)
- Supporting screenshots and evidence in `reports/`

---

## 20. Execution Summary

### Round 1 Summary
- 12 test cases executed: 11 passed, 1 failed
- Pass rate: 91.7%
- Critical security finding: IDOR vulnerability on notification settings endpoint (promoted to bug report — major)
- Notification system bugs identified:
  - Non-aggregated module open events cause notification flood (promoted to bug report — minor)
  - Hardcoded localhost URL in email template (promoted to bug report — minor)
- Preference-gated delivery, transactional email, settings API validation, and settings page persistence all verified successfully
