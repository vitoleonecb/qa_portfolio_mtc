# API Test Automation

Automated API tests using Python + `requests` + `pytest`.

## Setup

```bash
pip install requests pytest python-dotenv
```

### Environment Configuration

```bash
cp automation/.env.example automation/.env
```

Edit `automation/.env` with your test credentials and URLs. The `.env` file is gitignored — only `.env.example` is committed.

## Running Tests

```bash
# All API tests
pytest automation/api/ -v

# Auth tests only
pytest automation/api/auth/auth_script.py -v

# Module tests only
pytest automation/api/modules/module-script.py -v

# Notification tests only
pytest automation/api/notifications/notifications-script.py -v
```

## Prerequisites

- Backend running on `http://localhost:3036`
- Test user accounts exist (see `docs/environment-setup.md`)
- MySQL and Redis running

## Test Coverage

### Auth (`auth/auth_script.py`)
- Valid and invalid login
- Empty credential validation
- Protected route JWT enforcement (no token, invalid token, expired token)
- Admin vs. non-admin authorization
- Forgot password non-enumeration behavior

### Modules (`modules/module-script.py`)
- Admin-only module creation
- Status transition validation (including known bug BUG-MOD-001)
- Scheduler guardrails

### Notifications (`notifications/notifications-script.py`)
- Settings API read and write
- Input validation (invalid channel, non-boolean sub-options)
- IDOR authorization check (known bug BUG-NOTIF-003)

## Configuration

All scripts read from `automation/.env` via the shared `conftest.py`. Update the `.env` file to match your environment — no need to edit individual scripts.
