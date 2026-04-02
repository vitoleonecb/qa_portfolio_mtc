"""Auth UI Tests (Playwright)

End-to-end UI tests for authentication flows including login,
logout, validation, and auth state behavior.

Usage:
    pytest auth.spec.py -v

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


# --- Login Tests ---

class TestLogin:
    """Login page UI behavior."""

    def test_valid_login_redirects_to_showcases(self, page: Page):
        page.goto(f"{BASE_URL}/login")
        page.fill('input[type="text"]', VALID_EMAIL)
        page.fill('input[type="password"]', VALID_PASSWORD)
        page.click('button:has-text("Log In")')
        page.wait_for_url(f"{BASE_URL}/showcases")
        assert "/showcases" in page.url

    def test_invalid_login_shows_error(self, page: Page):
        page.goto(f"{BASE_URL}/login")
        page.fill('input[type="text"]', VALID_EMAIL)
        page.fill('input[type="password"]', "WrongPassword")
        page.click('button:has-text("Log In")')
        error = page.locator("text=Invalid email/username or password")
        expect(error).to_be_visible()
        assert "/login" in page.url

    def test_empty_email_shows_validation_error(self, page: Page):
        page.goto(f"{BASE_URL}/login")
        page.fill('input[type="password"]', VALID_PASSWORD)
        page.click('button:has-text("Log In")')
        error = page.locator("text=Please enter your email or username")
        expect(error).to_be_visible()

    def test_empty_password_shows_validation_error(self, page: Page):
        page.goto(f"{BASE_URL}/login")
        page.fill('input[type="text"]', VALID_EMAIL)
        page.click('button:has-text("Log In")')
        error = page.locator("text=Please enter your password")
        expect(error).to_be_visible()


# --- Logout Tests ---

class TestLogout:
    """Logout and session cleanup."""

    def test_logout_clears_session_and_redirects(self, page: Page):
        # Log in first
        page.goto(f"{BASE_URL}/login")
        page.fill('input[type="text"]', VALID_EMAIL)
        page.fill('input[type="password"]', VALID_PASSWORD)
        page.click('button:has-text("Log In")')
        page.wait_for_url(f"{BASE_URL}/showcases")

        # Navigate to profile and log out
        page.goto(f"{BASE_URL}/profile")
        page.click('button:has-text("Log Out")')
        page.wait_for_url(f"{BASE_URL}/login")
        assert "/login" in page.url

        # Verify token is cleared
        token = page.evaluate("localStorage.getItem('accessToken')")
        assert token is None


# --- Auth State Tests ---

class TestAuthState:
    """UI state reflects authentication status."""

    def test_unauthenticated_user_redirected_from_profile(self, page: Page):
        page.goto(f"{BASE_URL}/profile")
        page.wait_for_url(f"{BASE_URL}/login")
        assert "/login" in page.url

    def test_avatar_hidden_when_logged_out(self, page: Page):
        page.goto(f"{BASE_URL}/login")
        avatar = page.locator("[class*='avatar']")
        expect(avatar).to_have_count(0)
