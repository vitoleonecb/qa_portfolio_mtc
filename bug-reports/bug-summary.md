# Bug Report Summary

This document summarizes all defects identified during test execution.

---

## Overview

| Severity | Count | Bug IDs |
|----------|-------|---------|
| Critical (P0) | 1 | TC-AUTH-014 |
| Major (P1) | 3 | BUG-MOD-001, BUG-NOTIF-003, BUG-AUTH-001 |
| Medium (P2) | 3 | BUG-NOTIF-001, BUG-NOTIF-002, BUG-AUTH-002 |
| **Total** | **7** | |

---

## Bug Index

### Critical

**TC-AUTH-014 — Auth State Not Invalidated After Token Expiration**
- Feature: Authentication
- Expired JWT sessions leave the UI in an authenticated state. No global interceptor clears auth state on 401/403 responses.
- [Full report](critical.md)

### Major

**BUG-AUTH-001 — Admin Authorization Returns 403 for Valid Credentials**
- Feature: Authentication
- Valid admin credentials are rejected with `403 Forbidden` on all admin-protected endpoints. The admin authorization middleware is not correctly resolving or validating the role claim from the JWT.
- [Full report](major.md#bug-auth-001--admin-authorization-returns-403-for-valid-credentials)

**BUG-MOD-001 — Module Status Endpoint Accepts Invalid Values**
- Feature: Modules
- The status update endpoint accepts arbitrary strings (e.g., `"banana"`) without validation, risking data integrity across UI, scheduler, and analytics.
- [Full report](major.md#bug-mod-001--module-status-endpoint-accepts-invalid-values)

**BUG-NOTIF-003 — IDOR: Unauthorized Modification of Notification Settings**
- Feature: Notifications
- Any authenticated user can modify another user's notification preferences via API. The endpoint checks authentication but not resource ownership.
- [Full report](major.md#bug-notif-003--idor-unauthorized-modification-of-notification-settings)

### Medium

**BUG-AUTH-002 — Admin Endpoints Return Plain Text Instead of JSON**
- Feature: Authentication
- Admin endpoint responses use plain text instead of JSON, causing `JSONDecodeError` in API clients and automated tests. Violates the API contract expected across all other routes.
- [Full report](minor.md#bug-auth-002--admin-endpoints-return-plain-text-instead-of-json)

**BUG-NOTIF-001 — Notification Flood from Non-Aggregated Module Open Events**
- Feature: Notifications
- Simultaneous module opens produce one email per module instead of a single aggregated notification per workshop cycle.
- [Full report](minor.md#bug-notif-001--notification-flood-from-non-aggregated-module-open-events)

**BUG-NOTIF-002 — Incorrect Frontend URL in Notification Email Template**
- Feature: Notifications
- Email templates contain hardcoded `localhost` URLs, rendering links unusable outside the local development environment.
- [Full report](minor.md#bug-notif-002--incorrect-frontend-url-in-notification-email-template)

---

## Distribution by Feature

| Feature | Critical | Major | Medium | Total |
|---------|----------|-------|--------|-------|
| Authentication | 1 | 1 | 1 | 3 |
| Modules | 0 | 1 | 0 | 1 |
| Notifications | 0 | 1 | 2 | 3 |
| **Total** | **1** | **3** | **3** | **7** |

---

## Notes
- All bugs were discovered through manual testing and API inspection
- The IDOR vulnerability (BUG-NOTIF-003) is the highest-priority security finding
- Auth state invalidation (TC-AUTH-014) has the broadest user-facing impact
- Notification bugs (BUG-NOTIF-001, BUG-NOTIF-002) are lower priority but affect production readiness
