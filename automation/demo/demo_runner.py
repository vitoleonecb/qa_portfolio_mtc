"""90-Second QA Demo Runner.

Drives a scripted 90-second walkthrough of the mtc3portal application
using Playwright (headed Chromium) for the UI side and Python `requests`
for out-of-band API calls. Every request/response is streamed to a
colorized terminal log (`terminal_log.TerminalLog`) so a screen
recording of the browser window plus the terminal tells the full story.

Run directly:
    python automation/demo/demo_runner.py

Or via pytest:
    pytest automation/demo/ -v

Prerequisites:
    - Backend running on http://localhost:3036
    - Frontend running on http://localhost:5173
    - Seeded user/admin/user_B accounts (see docs/environment-setup.md)
    - `automation/.env` populated (USER_EMAIL/PASSWORD, USER_B_*, etc.)
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# Make sibling automation/ modules importable (conftest, api helpers).
_AUTOMATION_ROOT = Path(__file__).resolve().parents[1]
if str(_AUTOMATION_ROOT) not in sys.path:
    sys.path.insert(0, str(_AUTOMATION_ROOT))

import requests
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

from conftest import (  # type: ignore  # noqa: E402
    API_BASE_URL,
    FRONTEND_BASE_URL,
    USER_EMAIL,
    USER_PASSWORD,
    USER_B_EMAIL,
    USER_B_PASSWORD,
    WORKSHOP_ID,
)

# Local package import (works when run as module or script).
try:
    from .terminal_log import TerminalLog  # type: ignore
except ImportError:
    from terminal_log import TerminalLog  # type: ignore


# --- Configuration --------------------------------------------------------

SLOWMO_MS = int(os.getenv("DEMO_SLOWMO_MS", "350"))
HEADLESS = os.getenv("DEMO_HEADLESS", "0") == "1"

# ---- Split-screen window geometry ---------------------------------------
# Layout is designed for a 1920-wide display carved into 7 columns (~274px):
#   | terminal (~1/7) | User A window (~4/7) | User B window (~2/7) |
# The terminal slot is reserved for the user's shell — we only position the
# two browser windows. All four DEMO_*_WINDOW_* vars can be overridden from
# the environment. Viewport values are slightly smaller than the window size
# to account for Chromium chrome (tabs + address bar).

USER_A_WINDOW_POS = os.getenv("DEMO_A_WINDOW_POS", "274,80")
USER_A_WINDOW_SIZE = os.getenv("DEMO_A_WINDOW_SIZE", "1097,960")
USER_B_WINDOW_POS = os.getenv("DEMO_B_WINDOW_POS", "1371,80")
USER_B_WINDOW_SIZE = os.getenv("DEMO_B_WINDOW_SIZE", "548,960")


def _parse_wh(value: str, fallback: tuple[int, int]) -> dict:
    try:
        w, h = value.lower().replace("x", ",").split(",")
        return {"width": int(w), "height": int(h)}
    except Exception:
        return {"width": fallback[0], "height": fallback[1]}


VIEWPORT_A = _parse_wh(os.getenv("DEMO_VIEWPORT_A", "1090x870"), (1090, 870))
VIEWPORT_B = _parse_wh(os.getenv("DEMO_VIEWPORT_B", "540x870"), (540, 870))

TOTAL_SCENES = 9


# --- Runner ---------------------------------------------------------------

@dataclass
class DemoResult:
    elapsed_seconds: float
    request_count: int
    error_count: int
    bug_count: int


class DemoRunner:
    """Orchestrates the 90-second demo."""

    def __init__(self, log: Optional[TerminalLog] = None):
        self.log = log or TerminalLog()
        self.session = requests.Session()
        self.user_token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.user_b_token: Optional[str] = None
        self.user_b_id: Optional[int] = None

    # ---- API helpers (log every call) ----

    def _api(self, method: str, path: str, tag: str = "source=script", **kwargs) -> requests.Response:
        url = f"{API_BASE_URL}{path}"
        started = time.monotonic()
        resp = self.session.request(method, url, timeout=10, **kwargs)
        elapsed_ms = (time.monotonic() - started) * 1000
        snippet = None
        try:
            # Small, safe snippet of the JSON body if present.
            text = resp.text or ""
            snippet = text[:200] if text else None
        except Exception:
            snippet = None
        self.log.request(
            method=method.upper(),
            path=_short_path(url),
            status=resp.status_code,
            ms=elapsed_ms,
            snippet=snippet,
            tag=tag,
        )
        return resp

    def _login_api(self, email: str, password: str, tag: str) -> Optional[dict]:
        resp = self._api("POST", "/users/login", tag=tag, json={"email": email, "password": password})
        if resp.status_code == 200:
            return resp.json()
        return None

    def _showcase_for_workshop(self, workshop_id: int) -> Optional[int]:
        """Look up which showcase contains the target workshop so scene 8 can
        click through the real navigation hierarchy.

        Requires the User A token (we already captured it in scene 4).
        """
        if not self.user_token:
            return None
        try:
            resp = self._api(
                "GET",
                f"/workshops/{workshop_id}",
                tag="setup:route",
                headers={"Authorization": f"Bearer {self.user_token}"},
            )
            data = resp.json()
            row = data[0] if isinstance(data, list) and data else data
            if isinstance(row, dict) and row.get("showcase_id") is not None:
                return int(row["showcase_id"])
        except Exception:
            pass
        return None

    # ---- Playwright lifecycle hooks ----

    def _attach_network_hooks(self, page, tag: str = "source=ui") -> None:
        """Mirror every API request/response into the terminal log.

        `tag` lets callers distinguish multiple browser contexts (User A vs B).
        """
        pending: dict[str, float] = {}

        def on_request(request):
            if "/api/" not in request.url:
                return
            pending[request.url + ":" + request.method] = time.monotonic()

        def on_response(response):
            if "/api/" not in response.url:
                return
            key = response.url + ":" + response.request.method
            ms = None
            started = pending.pop(key, None)
            if started is not None:
                ms = (time.monotonic() - started) * 1000
            snippet = None
            try:
                ct = response.header_value("content-type") or ""
                if "application/json" in ct or "text" in ct:
                    body = response.text()
                    snippet = body[:200] if body else None
            except Exception:
                snippet = None
            self.log.request(
                method=response.request.method,
                path=_short_path(response.url),
                status=response.status,
                ms=ms,
                snippet=snippet,
                tag=tag,
            )

        page.on("request", on_request)
        page.on("response", on_response)

    # ---- Scenes ----

    def scene_intro(self, page) -> None:
        self.log.scene("Opening login page", index=1, total=TOTAL_SCENES)
        self.log.note("Demo starting.")
        page.goto(f"{FRONTEND_BASE_URL}/login")
        page.wait_for_load_state("domcontentloaded")
        _pause(6.0)

    def scene_empty_field_validation(self, page) -> None:
        self.log.scene("Empty-field frontend validation", index=2, total=TOTAL_SCENES)
        self.log.note("Submitting with no password to trigger client-side validation.")
        try:
            page.fill('input[type="text"]', USER_EMAIL)
            _hover_click(page, 'input[type="submit"].logInButton')
            # The frontend shows an inline validation message — no API call fires.
            try:
                page.wait_for_selector("text=Please enter your password", timeout=2500)
                self.log.success("Frontend blocked submit (no API call fired).")
            except PWTimeoutError:
                self.log.warn("Validation message not detected; UI may have changed.")
        except Exception as exc:
            self.log.warn(f"Scene 2 soft-fail: {exc}")
        _pause(5.0)

    def scene_wrong_password(self, page) -> None:
        self.log.scene("Wrong password → 401", index=3, total=TOTAL_SCENES)
        self.log.note("Submitting a wrong password. Expect a red 401 in the log.")
        try:
            page.fill('input[type="text"]', USER_EMAIL)
            page.fill('input[type="password"]', "WrongPassword!")
            _hover_click(page, 'input[type="submit"].logInButton')
            try:
                page.wait_for_selector("text=Invalid email/username or password", timeout=3000)
                self.log.success("UI displays defensive error message.")
            except PWTimeoutError:
                self.log.warn("Error message not visible; continuing.")
        except Exception as exc:
            self.log.warn(f"Scene 3 soft-fail: {exc}")
        _pause(5.0)

    def scene_valid_login(self, page) -> None:
        self.log.scene("Valid login → token issued", index=4, total=TOTAL_SCENES)
        try:
            page.fill('input[type="text"]', USER_EMAIL)
            page.fill('input[type="password"]', USER_PASSWORD)
            _hover_click(page, 'input[type="submit"].logInButton')
            page.wait_for_url(f"{FRONTEND_BASE_URL}/showcases", timeout=6000)
            token = page.evaluate("localStorage.getItem('accessToken')")
            if token:
                self.user_token = token
                self.log.success("Access token stored in localStorage.")
            # Grab user_id directly from API (one call) so we can do IDOR scene.
            data = self._login_api(USER_EMAIL, USER_PASSWORD, tag="source=script")
            if data:
                self.user_id = data.get("user", {}).get("user_id")
                self.user_token = self.user_token or data.get("accessToken")
        except Exception as exc:
            self.log.warn(f"Scene 4 soft-fail: {exc}")
        _pause(5.0)

    def scene_profile_and_settings(self, page) -> None:
        self.log.scene("Profile page + notification settings", index=5, total=TOTAL_SCENES)
        try:
            # Click the account avatar in the header so the navigation is
            # visibly a user action, not a raw URL change.
            self.log.note("Hovering account avatar before clicking into /profile.")
            _hover_click(page, 'a[aria-label="Account settings"]')
            page.wait_for_url(f"{FRONTEND_BASE_URL}/profile", timeout=5000)
            page.wait_for_load_state("domcontentloaded", timeout=5000)
            page.wait_for_timeout(800)
        except Exception as exc:
            self.log.warn(f"Profile navigation soft-fail: {exc}")
        if self.user_token and self.user_id:
            self._api(
                "GET",
                f"/users/{self.user_id}/notification-settings",
                tag="source=script",
                headers={"Authorization": f"Bearer {self.user_token}"},
            )
        else:
            self.log.warn("Skipping settings GET — token/user_id unavailable.")
        _pause(5.0)

    def scene_input_validation(self, page) -> None:
        self.log.scene("Defensive input validation (400s)", index=6, total=TOTAL_SCENES)
        # Scroll User A's /profile into the notifications section BEFORE the
        # validation PUTs fire, so the affected UI is in frame throughout this
        # and the IDOR scene that follows.
        _scroll_to_percent(page, 0.8)
        if not (self.user_token and self.user_id):
            self.log.warn("Skipping — no user token.")
            _pause(1.5)
            return

        headers = {"Authorization": f"Bearer {self.user_token}"}
        valid_base = {
            "channel": "email",
            "module_open": True,
            "last_day_reminder": True,
            "materials_ready": True,
            "workshop_rsvp": True,
            "showcase_announcements": True,
            "showcase_ticket": True,
        }

        self.log.note("PUT with channel=\"telegram\" — should be rejected.")
        self._api(
            "PUT",
            f"/users/{self.user_id}/notification-settings",
            tag="neg-test",
            headers=headers,
            json={**valid_base, "channel": "telegram"},
        )
        _pause(4.0)

        self.log.note('PUT with module_open="yes" (non-boolean) — should be rejected.')
        self._api(
            "PUT",
            f"/users/{self.user_id}/notification-settings",
            tag="neg-test",
            headers=headers,
            json={**valid_base, "module_open": "yes"},
        )
        _pause(5.0)

    def scene_idor(self, pw, page) -> None:
        self.log.scene("IDOR check — user A writes user B's settings", index=7, total=TOTAL_SCENES)

        # 1. Log User B in via API purely to capture token + user_id for the
        # IDOR target path (UI login happens below, visible on camera).
        data = self._login_api(USER_B_EMAIL, USER_B_PASSWORD, tag="setup:user_b")
        if data:
            self.user_b_token = data.get("accessToken")
            self.user_b_id = data.get("user", {}).get("user_id")
        if not (self.user_token and self.user_b_token and self.user_b_id):
            self.log.warn("Skipping IDOR scene — missing credentials.")
            _pause(1.5)
            return

        # 2. Spin up a second headed Chromium window on the right side of the
        # screen so User B can log in through the real UI on camera.
        browser_b = pw.chromium.launch(
            headless=HEADLESS,
            slow_mo=SLOWMO_MS,
            args=[
                f"--window-position={USER_B_WINDOW_POS}",
                f"--window-size={USER_B_WINDOW_SIZE}",
            ],
        )
        context_b = browser_b.new_context(viewport=VIEWPORT_B)
        page_b = context_b.new_page()
        self._attach_network_hooks(page_b, tag="source=ui-B")

        try:
            # UI login for User B: go to /login, type credentials, hover the
            # submit input so the press is obvious, then click.
            self.log.note("User B opens /login on the right and types their credentials.")
            page_b.goto(f"{FRONTEND_BASE_URL}/login")
            page_b.wait_for_load_state("domcontentloaded", timeout=5000)
            page_b.fill('input[type="text"]', USER_B_EMAIL)
            page_b.fill('input[type="password"]', USER_B_PASSWORD)
            _hover_click(page_b, 'input[type="submit"].logInButton')
            page_b.wait_for_url(f"{FRONTEND_BASE_URL}/showcases", timeout=6000)

            # Navigate to /profile via the account avatar (not a raw goto) so
            # the icon press is visible too.
            self.log.note("User B clicks the account avatar to open their profile.")
            _hover_click(page_b, 'a[aria-label="Account settings"]')
            page_b.wait_for_url(f"{FRONTEND_BASE_URL}/profile", timeout=5000)
            page_b.wait_for_load_state("domcontentloaded", timeout=5000)
            page_b.wait_for_timeout(600)
            _scroll_to_percent(page_b, 0.8)
            self.log.note("User B's profile is rendered on the right — note their current settings.")
            _pause(2.0)

            # 3. Show both tokens + user_ids so the viewer sees the attacker
            # (User A) using their own token to hit User B's resource path.
            self.log.highlight(
                "USER A (attacker)",
                f"user_id={self.user_id}  token={_trunc_token(self.user_token)}",
            )
            self.log.highlight(
                "USER B (victim)  ",
                f"user_id={self.user_b_id}  token={_trunc_token(self.user_b_token)}",
            )
            _pause(1.5)

            # 4. Perform the cross-user PUT with a visibly different payload so
            # the post-reload UI change is obvious.
            idor_payload = {
                "channel": "sms",
                "module_open": False,
                "last_day_reminder": False,
                "materials_ready": True,
                "workshop_rsvp": True,
                "showcase_announcements": True,
                "showcase_ticket": True,
            }
            resp = self._api(
                "PUT",
                f"/users/{self.user_b_id}/notification-settings",
                tag="idor",
                headers={"Authorization": f"Bearer {self.user_token}"},
                json=idor_payload,
            )
            if resp.status_code == 200:
                self.log.bug(
                    "BUG-NOTIF-003",
                    "IDOR: User A wrote User B's settings. Expected 403, got 200.",
                )
            elif resp.status_code == 403:
                self.log.success("Fix detected — endpoint now returns 403 on cross-user writes.")
            _pause(2.0)

            # 5. Reload User B's page — the re-fetched settings GET shows the
            # attacker-written values; both the UI and the log line prove it.
            self.log.note("Reloading User B's profile — the refetched GET will show attacker-written values.")
            page_b.reload()
            page_b.wait_for_load_state("domcontentloaded", timeout=5000)
            page_b.wait_for_timeout(800)
            _scroll_to_percent(page_b, 0.8)
            _pause(3.5)
        finally:
            context_b.close()
            browser_b.close()

    def scene_modules(self, page) -> None:
        self.log.scene("Workshop modules page", index=8, total=TOTAL_SCENES)
        # Walk the viewer through the app's navigation structure instead of
        # jumping straight to the modules URL: nav menu → showcases → one
        # showcase → a workshop inside it.
        try:
            # 1. Open the hamburger nav menu.
            self.log.note("Opening the hamburger nav menu.")
            _hover_click(page, 'div.menuIcon:not(.accountMenuIcon)')
            page.wait_for_url(f"{FRONTEND_BASE_URL}/nav", timeout=4000)
            page.wait_for_load_state("domcontentloaded", timeout=4000)
            page.wait_for_timeout(800)

            # 2. Pick the Showcases nav card. The fixed header overlays the
            # top of the grid, so we force the click past it.
            self.log.note("Selecting the Showcases nav card.")
            _hover_click(
                page,
                '.navOptions a[href="/showcases"]',
                force=True,
            )
            page.wait_for_url(f"{FRONTEND_BASE_URL}/showcases", timeout=5000)
            page.wait_for_load_state("domcontentloaded", timeout=4000)
            page.wait_for_timeout(600)
            _scroll_to_percent(page, 0.25)

            # 3. Open the showcase that contains workshop WORKSHOP_ID.
            showcase_id = self._showcase_for_workshop(WORKSHOP_ID)
            if showcase_id is None:
                self.log.warn(
                    f"Could not resolve showcase for workshop {WORKSHOP_ID}; "
                    f"falling back to direct navigation."
                )
                page.goto(f"{FRONTEND_BASE_URL}/workshops/{WORKSHOP_ID}/modules")
            else:
                self.log.note(f"Opening showcase {showcase_id}.")
                _hover_click(page, f'a[href="/showcases/{showcase_id}"]')
                page.wait_for_url(
                    f"{FRONTEND_BASE_URL}/showcases/{showcase_id}", timeout=5000
                )
                page.wait_for_load_state("domcontentloaded", timeout=4000)
                page.wait_for_timeout(600)
                # Scroll down just enough to reveal the Workshops section.
                _scroll_to_percent(page, 0.5)

                # 4. Click the workshop card that targets workshop WORKSHOP_ID.
                self.log.note(f"Clicking workshop {WORKSHOP_ID} to open its modules page.")
                _hover_click(
                    page, f'a[href="/workshops/{WORKSHOP_ID}/modules"]'
                )
                page.wait_for_url(
                    f"{FRONTEND_BASE_URL}/workshops/{WORKSHOP_ID}/modules",
                    timeout=5000,
                )

            page.wait_for_load_state("domcontentloaded", timeout=5000)
            page.wait_for_timeout(1000)
            self.log.note("Modules grouped by lifecycle status: pending → open → processing → completed.")
        except Exception as exc:
            self.log.warn(f"Modules navigation soft-fail: {exc}")
        _pause(3.5)

    def scene_logout(self, page) -> None:
        self.log.scene("Logout + session cleanup", index=9, total=TOTAL_SCENES)
        try:
            # Navigate back to /profile via the avatar so the final scene
            # keeps the same visual vocabulary as scene 5.
            self.log.note("Hovering account avatar to return to /profile.")
            _hover_click(page, 'a[aria-label="Account settings"]')
            page.wait_for_url(f"{FRONTEND_BASE_URL}/profile", timeout=5000)
            page.wait_for_load_state("domcontentloaded", timeout=4000)
            page.wait_for_timeout(600)
            # Scroll down so the Log Out button is clearly framed on camera.
            _scroll_to_percent(page, 1.0)
            self.log.note("Hovering the Log Out button before clicking it.")
            _hover_click(page, 'button:has-text("Log Out")')
            page.wait_for_url(f"{FRONTEND_BASE_URL}/login", timeout=5000)
            token = page.evaluate("localStorage.getItem('accessToken')")
            if token is None:
                self.log.success("accessToken cleared from localStorage; redirected to /login.")
            else:
                self.log.warn("accessToken still present after logout.")
        except Exception as exc:
            self.log.warn(f"Logout soft-fail: {exc}")
        _pause(3.0)

    # ---- Top-level orchestrate ----

    def preflight(self) -> None:
        try:
            r = self.session.get(f"{API_BASE_URL.rstrip('/').rsplit('/', 1)[0]}/health", timeout=3)
            self.log.info(f"Backend /health → {r.status_code}")
        except Exception as exc:
            self.log.error(
                f"Backend health check failed — start the backend before running the demo: {exc}"
            )
            raise SystemExit(1)

    def run(self) -> DemoResult:
        started = time.monotonic()
        # Stack cue — small on-camera hint so reviewers know what's driving
        # the browser without needing to open the source.
        self.log.highlight(
            "STACK",
            "Playwright + requests + pytest  ·  9 scenes  ·  ~90s",
        )
        self.preflight()

        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=HEADLESS,
                slow_mo=SLOWMO_MS,
                args=[
                    f"--window-position={USER_A_WINDOW_POS}",
                    f"--window-size={USER_A_WINDOW_SIZE}",
                ],
            )
            context = browser.new_context(viewport=VIEWPORT_A)
            page = context.new_page()
            self._attach_network_hooks(page, tag="source=ui-A")

            try:
                self.scene_intro(page)
                self.scene_empty_field_validation(page)
                self.scene_wrong_password(page)
                self.scene_valid_login(page)
                self.scene_profile_and_settings(page)
                self.scene_input_validation(page)
                self.scene_idor(pw, page)
                self.scene_modules(page)
                self.scene_logout(page)
            finally:
                elapsed = time.monotonic() - started
                self.log.outro(f"Demo finished in {elapsed:.1f}s (target ≤ 95s).")
                context.close()
                browser.close()

        return DemoResult(
            elapsed_seconds=time.monotonic() - started,
            request_count=self.log.request_count,
            error_count=self.log.error_count,
            bug_count=self.log.bug_count,
        )


# --- helpers --------------------------------------------------------------

def _short_path(url: str) -> str:
    """Trim hostname so the terminal shows `/api/...` lines."""
    try:
        parsed = urlparse(url)
        path = parsed.path or url
        if parsed.query:
            path = f"{path}?{parsed.query}"
        return path
    except Exception:
        return url


def _trunc_token(token: Optional[str], keep: int = 16) -> str:
    """Abbreviate a JWT for screen-friendly display."""
    if not token:
        return "<none>"
    if len(token) <= keep * 2 + 1:
        return token
    return f"{token[:keep]}…{token[-6:]}"


def _hover_click(
    page,
    selector: str,
    *,
    hover_ms: int = 1000,
    timeout: int = 3000,
    force: bool = False,
) -> None:
    """Hover a target, pause so the press is obvious, then click.

    Used for anything the viewer needs to see “about to happen” on camera:
    login submit, account-avatar icon, log-out button, etc. Pass
    `force=True` when the target sits under a sticky/fixed overlay that
    would otherwise intercept the pointer event.
    """
    try:
        page.hover(selector, timeout=timeout)
        page.wait_for_timeout(hover_ms)
        page.click(selector, timeout=timeout, force=force)
    except Exception:
        # Fall back to a blind (forced) click so a soft-fail doesn't kill the scene.
        try:
            page.click(selector, timeout=timeout, force=True)
        except Exception:
            pass


def _scroll_to_percent(page, pct: float) -> None:
    """Smooth-scroll the page to a fraction of the document height.

    Used in the IDOR scene to bring the notifications section into view on
    both the middle (User A) and right (User B) profile pages.
    """
    try:
        page.evaluate(
            "(p) => window.scrollTo({ top: document.body.scrollHeight * p, behavior: 'smooth' })",
            pct,
        )
        # Give the smooth scroll a beat to complete before the next action.
        page.wait_for_timeout(600)
    except Exception:
        pass


def _pause(seconds: float) -> None:
    """Sleep in small increments so the UI has time to update."""
    time.sleep(max(0.0, seconds))


# --- Entrypoint -----------------------------------------------------------

def main() -> int:
    runner = DemoRunner()
    result = runner.run()
    # Return non-zero if nothing defensive happened — the demo is not doing its job.
    if result.error_count < 3:
        runner.log.error(
            f"Only {result.error_count} error responses captured; demo must show defensive validation."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
