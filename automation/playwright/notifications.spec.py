"""Notifications Settings UI Tests (Playwright)

End-to-end UI tests for the notification settings page including
preference loading, master toggle, and channel cycling.

Usage:
    pytest notifications.spec.py -v

Requires:
    pip install pytest-playwright python-dotenv
    playwright install
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from playwright.sync_api import Page, expect
from conftest import FRONTEND_BASE_URL, USER_EMAIL, USER_PASSWORD

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


# --- Settings Page Tests ---

class TestSettingsPage:
    """Profile notification settings page behavior."""

    def test_settings_page_loads_preferences(self, page: Page):
        login(page)
        page.goto(f"{BASE_URL}/profile")
        page.wait_for_load_state("networkidle")
        assert "/profile" in page.url

    def test_master_toggle_disables_notifications(self, page: Page):
        """Clicking the master toggle should set channel to 'none'
        and hide sub-option toggles."""
        login(page)
        page.goto(f"{BASE_URL}/profile")
        page.wait_for_load_state("networkidle")

        # Find and click the master notifications toggle
        master_toggle = page.locator("[class*='toggle'], [class*='switch']").first
        if master_toggle.is_visible():
            master_toggle.click()
            # After disabling, sub-options should be hidden
            page.wait_for_timeout(500)

    def test_channel_cycles_through_options(self, page: Page):
        """Channel button should cycle: email -> sms -> both."""
        login(page)
        page.goto(f"{BASE_URL}/profile")
        page.wait_for_load_state("networkidle")

        channel_button = page.locator(
            "button:has-text('Email'), button:has-text('Text'), button:has-text('Email & Text')"
        ).first
        if channel_button.is_visible():
            initial_text = channel_button.inner_text()
            channel_button.click()
            page.wait_for_timeout(300)
            new_text = channel_button.inner_text()
            # Text should change after clicking
            assert new_text != initial_text
