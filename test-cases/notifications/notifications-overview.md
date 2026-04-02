# Notifications Overview

## Feature Summary
The notifications feature manages transactional and preference-based communication across email and SMS channels. It includes notification routing, user preference storage, frontend settings management, and worker-driven delivery for workshop and showcase events.

## Key User Flows
- User registers and receives transactional email
- User updates channel and sub-option preferences
- System sends module/workshop/showcase notifications based on saved settings
- Settings page loads and persists notification choices

## Key Components
- Backend: settings API, worker jobs, notification service
- Frontend: registration notification step, profile settings page
- Integrations: Postmark for email, Twilio for SMS
- Queue/worker: BullMQ notification processing

## Critical Logic
- Transactional notifications bypass preferences
- Preference-gated notifications respect channel and sub-option settings
- Settings API must validate payloads and enforce authorization
- UI state must match saved notification settings

## Risks / Complexity Areas
- Missing ownership validation on settings update
- Mismatched defaults across DB, registration, and settings page
- SMS formatting and delivery assumptions
- Worker branching by notification type and user eligibility

## Testing Focus
- Settings API validation
- Authorization on settings updates
- Transactional email behavior
- Preference-gated routing
- Settings persistence and UI hydration
