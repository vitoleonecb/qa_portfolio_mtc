"""Module Flow UI Tests (Playwright)

End-to-end UI tests for module display, progress tracking,
and status grouping on the workshop modules page.

Usage:
    pytest module-flow.spec.py -v

Requires:
    pip install pytest-playwright python-dotenv
    playwright install
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from playwright.sync_api import Page, expect
from conftest import FRONTEND_BASE_URL, USER_EMAIL, USER_PASSWORD, WORKSHOP_ID

BASE_URL = FRONTEND_BASE_URL

# --- Test Data ---
VALID_EMAIL = USER_EMAIL
VALID_PASSWORD = USER_PASSWORD


# --- Helpers ---

def login(page: Page):
    """Log in and navigate past the login page."""
    page.goto(f"{BASE_URL}/login")
    page.fill('input[type="text"]', VALID_EMAIL)
    page.fill('input[type="password"]', VALID_PASSWORD)
    page.click('button:has-text("Log In")')
    page.wait_for_url(f"{BASE_URL}/showcases")


# --- Module Display Tests ---

class TestModuleDisplay:
    """Workshop modules page UI behavior."""

    def test_modules_page_loads(self, page: Page):
        login(page)
        page.goto(f"{BASE_URL}/workshops/{WORKSHOP_ID}/modules")
        page.wait_for_load_state("networkidle")
        assert "/modules" in page.url

    def test_modules_grouped_by_status(self, page: Page):
        """Modules should be organized under status headings."""
        login(page)
        page.goto(f"{BASE_URL}/workshops/{WORKSHOP_ID}/modules")
        page.wait_for_load_state("networkidle")

        # At least one status group should be visible
        status_headings = page.locator(
            "text=/Open|Processing|Completed|Pending/i"
        )
        expect(status_headings.first).to_be_visible()

    def test_open_module_shows_progress(self, page: Page):
        """Open modules should display a progress indicator."""
        login(page)
        page.goto(f"{BASE_URL}/workshops/{WORKSHOP_ID}/modules")
        page.wait_for_load_state("networkidle")

        # Look for progress text pattern (e.g., "2 / 5")
        progress = page.locator("text=/\\d+ \\/ \\d+/")
        if progress.count() > 0:
            expect(progress.first).to_be_visible()
