# UI Test Automation (Playwright)

Automated UI tests using Python Playwright + `pytest`.

## Setup

```bash
pip install pytest-playwright python-dotenv
playwright install
```

### Environment Configuration

```bash
cp automation/.env.example automation/.env
```

Edit `automation/.env` with your test credentials and URLs. The `.env` file is gitignored — only `.env.example` is committed.

## Running Tests

```bash
# All UI tests
pytest automation/playwright/ -v

# Auth UI tests only
pytest automation/playwright/auth.spec.py -v

# Module flow tests only
pytest automation/playwright/module-flow.spec.py -v

# Notification settings tests only
pytest automation/playwright/notifications.spec.py -v

# Run headed (visible browser)
pytest automation/playwright/auth.spec.py -v --headed
```

## Prerequisites

- Frontend running on `http://localhost:5173`
- Backend running on `http://localhost:3036`
- Test user accounts exist (see `docs/environment-setup.md`)

## Test Coverage

### Auth (`auth.spec.py`)
- Valid login with redirect verification
- Invalid login error message
- Empty field frontend validation
- Logout session cleanup and redirect
- Unauthenticated redirect to login
- Avatar visibility based on auth state

### Module Flow (`module-flow.spec.py`)
- Modules page loads correctly
- Modules grouped by status headings
- Progress indicator visible for open modules

### Notifications (`notifications.spec.py`)
- Settings page loads saved preferences
- Master toggle disables all notifications
- Channel button cycles through options

## Configuration

All specs read from `automation/.env` via the shared `conftest.py`. Update the `.env` file to match your environment — no need to edit individual spec files.
