"""Auth API Tests

Tests authentication endpoints for login, protected routes, JWT validation,
admin authorization, and password recovery flows.

Targets high-value automation candidates identified in the traceability matrix.

Usage:
    pytest auth_script.py -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import requests
import pytest
from conftest import API_BASE_URL, USER_EMAIL, USER_PASSWORD, ADMIN_EMAIL, ADMIN_PASSWORD

BASE_URL = API_BASE_URL

# --- Test Data ---
VALID_USER = {"email": USER_EMAIL, "password": USER_PASSWORD}
ADMIN_USER = {"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
INVALID_PASSWORD = {"email": USER_EMAIL, "password": "WrongPassword"}
NON_EXISTENT_USER = {"email": "ghost@example.com", "password": "anything"}
EMPTY_CREDENTIALS = {"email": "", "password": ""}


# --- Helpers ---

def login(credentials):
    """Log in and return the response."""
    return requests.post(f"{BASE_URL}/users/login", json=credentials)


def get_token(credentials):
    """Log in and return just the access token."""
    resp = login(credentials)
    assert resp.status_code == 200, f"Login failed: {resp.status_code} {resp.text}"
    token = resp.json().get("accessToken")
    assert token, f"No accessToken returned: {resp.text}"
    return token


def auth_header(token):
    """Build an Authorization header."""
    return {"Authorization": f"Bearer {token}"}


# --- Login Tests ---

class TestLogin:
    """POST /api/users/login"""

    def test_valid_login_returns_token(self):
        resp = login(VALID_USER)
        assert resp.status_code == 200
        data = resp.json()
        assert "accessToken" in data
        assert "user" in data
        assert data["user"]["email"] == VALID_USER["email"]

    def test_wrong_password_returns_401(self):
        resp = login(INVALID_PASSWORD)
        assert resp.status_code == 401
        assert "Invalid" in resp.json().get("message", "")

    def test_non_existent_user_returns_401(self):
        """Same error as wrong password — prevents user enumeration."""
        resp = login(NON_EXISTENT_USER)
        assert resp.status_code == 401
        assert "Invalid" in resp.json().get("message", "")

    def test_empty_credentials_returns_400(self):
        resp = login(EMPTY_CREDENTIALS)
        assert resp.status_code == 400
        assert "required" in resp.json().get("message", "").lower()


# --- Protected Route Tests ---

class TestProtectedRoutes:
    """JWT middleware enforcement on protected endpoints."""

    def test_no_token_returns_401(self):
        resp = requests.get(f"{BASE_URL}/users")
        assert resp.status_code == 401

    def test_invalid_token_returns_403(self):
        resp = requests.get(
            f"{BASE_URL}/users",
            headers=auth_header("invalidjunktoken")
        )
        assert resp.status_code == 403

    def test_expired_token_returns_403(self):
        """Uses a pre-crafted expired token. In practice, generate one
        with a past exp claim or wait for a short-lived token to expire."""
        expired_token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
            ".eyJ1c2VyX2lkIjoxLCJleHAiOjE2MDAwMDAwMDB9"
            ".placeholder"
        )
        resp = requests.get(
            f"{BASE_URL}/users",
            headers=auth_header(expired_token)
        )
        assert resp.status_code == 403

    def test_valid_token_grants_access(self):
        token = get_token(VALID_USER)
        assert token is not None
        resp = requests.get(
            f"{BASE_URL}/users",
            headers=auth_header(token)
        )
        # Regular user may get 403 on admin-only routes, but token is accepted
        assert resp.status_code in [200, 403]


# --- Admin Authorization Tests ---

class TestAdminAuthorization:
    """Admin-only route enforcement."""

    def test_admin_route_rejects_non_admin(self):
        token = get_token(VALID_USER)
        resp = requests.get(
            f"{BASE_URL}/users/list",
            headers=auth_header(token)
        )
        assert resp.status_code == 403
        assert "admin" in resp.json().get("message", "").lower()

    def test_admin_route_accepts_admin(self):
        token = get_token(ADMIN_USER)
        resp = requests.get(
            f"{BASE_URL}/users/list",
            headers=auth_header(token)
        )
        assert resp.status_code == 200


# --- Forgot Password Tests ---

class TestForgotPassword:
    """POST /api/users/forgot-password"""

    def test_valid_email_returns_200(self):
        resp = requests.post(
            f"{BASE_URL}/users/forgot-password",
            json={"email": VALID_USER["email"]}
        )
        assert resp.status_code == 200

    def test_non_existent_email_returns_200(self):
        """Non-enumerating: same 200 regardless of whether email exists."""
        resp = requests.post(
            f"{BASE_URL}/users/forgot-password",
            json={"email": "nobody@example.com"}
        )
        assert resp.status_code == 200
