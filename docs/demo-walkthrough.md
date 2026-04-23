# 90-Second QA Demo Walkthrough

▶ **[Watch the recorded demo on YouTube (1:30)](https://youtu.be/H5kjS0CREKc)**

A self-running, ~90-second scripted walkthrough of the application designed to be screen-recorded alongside a live terminal. It combines **Playwright** (headed Chromium) for the UI, **`requests`** for out-of-band API calls, and **`pytest`** as an optional entrypoint — reusing the same configuration and patterns as the rest of the portfolio automation.

---

## What this demo shows

The recording is designed to highlight QA coverage across the application — not a happy-path walkthrough. Each scene targets a different axis of testability:

- Frontend validation (empty-field submit blocked before an API call fires)
- Backend authentication rejection (wrong password → 401)
- Successful auth + JWT capture
- Authenticated GET of notification settings
- Backend input validation (invalid channel, non-boolean sub-option → 400)
- Known IDOR finding on notification settings (`BUG-NOTIF-003`)
- Module lifecycle display (status grouping)
- Session cleanup on logout

The terminal output color-codes every request/response: 2xx green, 4xx amber, 5xx red. Known bugs are tagged in red with their bug ID so they stand out in the recording.

---

## Scene timeline (≈90s)

| # | Time | Scene |
|---|------|-------|
| 1 | 0:00–0:08 | Open `/login`; scene banner "QA demo starting" |
| 2 | 0:08–0:16 | Empty password → frontend validation blocks submit |
| 3 | 0:16–0:25 | Wrong password → `POST /api/users/login → 401` |
| 4 | 0:25–0:33 | Valid credentials → 200, token captured, redirect to `/showcases` |
| 5 | 0:33–0:45 | Navigate to `/profile`; background `GET /users/:id/notification-settings` |
| 6 | 0:45–0:58 | Two negative PUTs: `channel:"telegram"` and `module_open:"yes"` → 400s |
| 7 | 0:58–1:12 | Second Chromium window opens as User B on `/profile`; User A PUTs cross-user settings; reload shows the attacker-written values → known IDOR (`BUG-NOTIF-003`) |
| 8 | 1:10–1:22 | Navigate to workshop modules page (status grouping visible) |
| 9 | 1:22–1:30 | Logout → token cleared → redirect to `/login`; outro banner |

Tables above are illustrative — wall-clock times depend on backend latency and `DEMO_SLOWMO_MS`.

---

## Bugs & validation exercised

- **BUG-NOTIF-003** — IDOR: user can write another user's notification settings. Scene 7 makes this visual: a second Chromium window signed in as User B sits next to User A's; User A fires a cross-user PUT with a deliberately divergent payload (`channel:"sms"`, two booleans flipped) and a subsequent `page_b.reload()` shows the attacker-written state in User B's UI while the terminal prints the `BUG-NOTIF-003` tag.
- **BUG-MOD-001** — Module status accepts arbitrary strings (covered by the existing API script, not re-exercised here to keep within 90s).
- Defensive validation: empty-field client check, 401 on bad credentials, 400 on invalid channel, 400 on non-boolean sub-option.

---

## How to run

### Prerequisites

- Backend running on `http://localhost:3036`
- Frontend running on `http://localhost:5173`
- Redis running (BullMQ worker optional for this demo)
- Seeded accounts (see [`environment-setup.md`](environment-setup.md)):
  - Regular user (`USER_EMAIL` / `USER_PASSWORD`)
  - Second user (`USER_B_EMAIL` / `USER_B_PASSWORD`) — required for the IDOR scene
- Python deps: `pytest-playwright`, `python-dotenv`, `requests` (already listed in the portfolio README)
- `playwright install` has been run at least once

### Configure `automation/.env`

The demo reuses the shared `automation/.env` loaded by `automation/conftest.py`. At minimum:

```
API_BASE_URL=http://localhost:3036/api
FRONTEND_BASE_URL=http://localhost:5173
USER_EMAIL=...
USER_PASSWORD=...
USER_B_EMAIL=...
USER_B_PASSWORD=...
WORKSHOP_ID=50
```

### Optional demo tuning

The default geometry targets a 1920×1080 display split into seven columns (~274 px each) so the whole recording fits edge-to-edge: terminal on the left (~1/7), User A window in the middle (~4/7), and the User B window (spawned for Scene 7) on the right (~2/7).

| Variable | Default | Purpose |
|----------|---------|---------|
| `DEMO_SLOWMO_MS` | `350` | Playwright `slow_mo` in ms — higher = more readable on video |
| `DEMO_HEADLESS` | `0` | Set to `1` to run headless (not recommended for a recording) |
| `DEMO_A_WINDOW_POS` | `274,80` | Screen position of the User A Chromium window |
| `DEMO_A_WINDOW_SIZE` | `1097,960` | Outer window size for User A |
| `DEMO_VIEWPORT_A` | `1090x870` | Viewport (content area) for User A — slightly less than window size to account for chrome |
| `DEMO_B_WINDOW_POS` | `1371,80` | Screen position of the User B window (opened during Scene 7) |
| `DEMO_B_WINDOW_SIZE` | `548,960` | Outer window size for User B |
| `DEMO_VIEWPORT_B` | `540x870` | Viewport (content area) for User B |

### Run as a script

```
python automation/demo/demo_runner.py
```

### Run under pytest

```
pytest automation/demo/ -v -s
```

`-s` lets the colorized stream flow live to your terminal — that's the output you want on camera.

---

## Recording tips

- Record the full screen. On a 1920×1080 display the defaults carve the screen into three tiles: `terminal | User A | User B` in a 1 : 4 : 2 ratio. Park your terminal in the leftmost ~274 px column and the two Chromium windows will slot in next to it.
- Override positioning / sizing if your display is different: `DEMO_A_WINDOW_POS`, `DEMO_A_WINDOW_SIZE`, `DEMO_VIEWPORT_A`, `DEMO_B_WINDOW_POS`, `DEMO_B_WINDOW_SIZE`, `DEMO_VIEWPORT_B`.
- Use a dark terminal theme so the green/amber/red pills pop.
- Start the recording just before launching the command — the first scene banner prints within ~1s.
- If you want more breathing room for annotations, bump `DEMO_SLOWMO_MS` (default is `350`) toward `450`–`500`.

---

## Source layout

- `automation/demo/demo_runner.py` — orchestrator (scenes, Playwright, requests)
- `automation/demo/terminal_log.py` — ANSI-colorized logger
- `automation/demo/test_demo.py` — pytest wrapper (duration + error-count assertions)
- `automation/demo/README.md` — quick-start for this folder

Helpers and config are reused from `automation/conftest.py`, and the demo respects the same credentials/URLs used by `automation/api/` and `automation/playwright/`.

---

## Non-goals

- This demo does **not** walk the ideal happy-path user lifecycle — that's a separate planned recording.
- No video recording / audio muxing is performed here; this script produces the deterministic on-screen experience, you run the screen recorder.
