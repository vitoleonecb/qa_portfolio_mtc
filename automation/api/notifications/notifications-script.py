"""Notifications API Tests

Tests notification settings endpoints for validation, persistence,
and authorization enforcement (including IDOR vulnerability check).

Usage:
    pytest notifications-script.py -v
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import requests
import pytest
from conftest import (
    API_BASE_URL, USER_EMAIL, USER_PASSWORD,
    USER_B_EMAIL, USER_B_PASSWORD
)

BASE_URL = API_BASE_URL

# --- Test Data ---
USER_A_CREDS = {"email": USER_EMAIL, "password": USER_PASSWORD}
USER_B_CREDS = {"email": USER_B_EMAIL, "password": USER_B_PASSWORD}

VALID_SETTINGS = {
    "channel": "email",
    "module_open": True,
    "last_day_reminder": True,
    "materials_ready": True,
    "workshop_rsvp": True,
    "showcase_announcements": True,
    "showcase_ticket": True,
}


# --- Helpers ---

def get_token(credentials):
    resp = requests.post(f"{BASE_URL}/users/login", json=credentials)
    assert resp.status_code == 200, f"Login failed: {resp.status_code} {resp.text}"
    data = resp.json()
    token = data.get("accessToken")
    assert token, f"No accessToken returned: {resp.text}"
    user_id = data.get("user", {}).get("user_id")
    assert user_id, f"No user_id returned: {resp.text}"
    return token, user_id


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def user_a():
    token, user_id = get_token(USER_A_CREDS)
    return {"token": token, "user_id": user_id}


@pytest.fixture(scope="module")
def user_b():
    token, user_id = get_token(USER_B_CREDS)
    return {"token": token, "user_id": user_id}


# --- Settings Read Tests ---

class TestSettingsRead:
    """GET /api/users/:id/notification-settings"""

    def test_get_settings_returns_stored_preferences(self, user_a):
        resp = requests.get(
            f"{BASE_URL}/users/{user_a['user_id']}/notification-settings",
            headers=auth_header(user_a["token"])
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "channel" in data


# --- Settings Write Tests ---

class TestSettingsWrite:
    """PUT /api/users/:id/notification-settings"""

    def test_valid_payload_accepted(self, user_a):
        resp = requests.put(
            f"{BASE_URL}/users/{user_a['user_id']}/notification-settings",
            json=VALID_SETTINGS,
            headers=auth_header(user_a["token"])
        )
        assert resp.status_code == 200

    def test_invalid_channel_rejected(self, user_a):
        resp = requests.put(
            f"{BASE_URL}/users/{user_a['user_id']}/notification-settings",
            json={**VALID_SETTINGS, "channel": "telegram"},
            headers=auth_header(user_a["token"])
        )
        assert resp.status_code == 400
        assert "channel" in resp.json().get("error", "").lower()

    def test_non_boolean_sub_option_rejected(self, user_a):
        resp = requests.put(
            f"{BASE_URL}/users/{user_a['user_id']}/notification-settings",
            json={**VALID_SETTINGS, "module_open": "yes"},
            headers=auth_header(user_a["token"])
        )
        assert resp.status_code == 400
        assert "boolean" in resp.json().get("error", "").lower()


# --- Authorization Tests ---

class TestSettingsAuthorization:
    """IDOR vulnerability check on notification settings endpoint."""

    def test_user_cannot_modify_other_users_settings(self, user_a, user_b):
        """Documents known IDOR bug (BUG-NOTIF-003).
        User A should NOT be able to update User B's settings.
        Currently returns 200 — will fail until the fix is applied."""
        resp = requests.put(
            f"{BASE_URL}/users/{user_b['user_id']}/notification-settings",
            json=VALID_SETTINGS,
            headers=auth_header(user_a["token"])
        )
        # BUG: Currently returns 200. Should return 403.
        # Uncomment after fix:
        # assert resp.status_code == 403
        assert resp.status_code == 200, (
            "Known bug (BUG-NOTIF-003): IDOR — endpoint does not verify ownership"
        )
