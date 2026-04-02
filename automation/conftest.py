"""Shared test configuration and fixtures.

Loads environment variables from automation/.env and provides
reusable fixtures for API and Playwright tests.

Requires:
    pip install python-dotenv
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the automation/ directory
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# --- Environment Variables ---

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3036/api")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")

USER_EMAIL = os.getenv("USER_EMAIL", "test@example.com")
USER_PASSWORD = os.getenv("USER_PASSWORD", "ValidPass1!")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "AdminPass1!")

USER_B_EMAIL = os.getenv("USER_B_EMAIL", "test2@example.com")
USER_B_PASSWORD = os.getenv("USER_B_PASSWORD", "ValidPass1!")

WORKSHOP_ID = int(os.getenv("WORKSHOP_ID", "50"))
