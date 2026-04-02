# Modules Overview

## Feature Summary
Modules represent structured units of a workshop where users respond to prompts. Each module progresses through lifecycle states (pending → open → processing → completed).

## Key User Flows
- Admin creates module → adds prompts → module scheduled
- User completes prompts → progresses through module
- Completion triggers RSVP eligibility

## Key Components
- Backend: module CRUD, status transitions, response handling
- Frontend: module list, progress bar, prompt pages, edge screens
- Scheduler: controls lifecycle transitions

## Critical Logic
- Status drives UI visibility and behavior
- Progress determines module completion
- Completion triggers RSVP creation

## Risks / Complexity Areas
- Status not validated → invalid states
- Progress tied to backend state → UI sync issues
- Dual RSVP creation paths
- Scheduler dependency for lifecycle

## Testing Focus
- Status transitions
- Response submission
- Progress tracking
- End-of-module flow
- Admin vs user permissions
