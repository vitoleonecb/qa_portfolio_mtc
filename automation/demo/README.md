# 90-Second QA Demo Orchestrator

Scripted Playwright + `requests` + `pytest` demo that drives the UI and API in parallel while a colorized terminal log captures every request/response. Designed to be screen-recorded with the browser and terminal side-by-side.

Full walkthrough, scene timeline, and recording tips live in [`../../docs/demo-walkthrough.md`](../../docs/demo-walkthrough.md).

---

## Quick start

```bash
# From qa_portfolio_mtc/
pip install pytest-playwright python-dotenv requests
playwright install

# Backend + frontend must be running, and automation/.env configured.

# Option A — run the orchestrator directly (recommended for recording):
python automation/demo/demo_runner.py

# Option B — run under pytest with live streaming:
pytest automation/demo/ -v -s
```

---

## Layout

- `demo_runner.py` — orchestrator: 9 scenes, ~90s, single Chromium window + `requests.Session`
- `terminal_log.py` — ANSI logger (green/amber/red status pills, scene banners, bug tags)
- `test_demo.py` — pytest wrapper asserting duration and defensive-error count
- `__init__.py` — package marker

## Environment overrides (optional)

| Var | Default | Purpose |
|-----|---------|---------|
| `DEMO_SLOWMO_MS` | `180` | Playwright `slow_mo` (ms) |
| `DEMO_HEADLESS` | `0` | Set `1` for headless (not for recording) |
| `DEMO_VIEWPORT` | `1280x800` | Browser viewport |

Shared credentials (`USER_EMAIL`, `USER_B_EMAIL`, `WORKSHOP_ID`, etc.) come from `automation/.env` via the top-level `automation/conftest.py`.
