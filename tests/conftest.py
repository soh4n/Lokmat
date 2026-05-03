"""
LokMat Tests — Shared fixtures for unit and integration tests.

Per GEMINI.md: pytest + pytest-asyncio for all test layers.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure the project root is in the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture(autouse=True, scope="function")
def use_local_jwt_auth():
    """
    Force local JWT authentication for all tests and reset shared state.

    1. Patches firebase_auth_enabled=False so local JWTs are accepted.
    2. Resets the _firebase_app global to prevent cross-test leakage.
    3. Clears rate limit counters so tests don't get 429 from previous runs.
    """
    import api.utils.auth as auth_module
    from api.utils.rate_limit import _counters

    # Reset Firebase global so it doesn't leak between tests
    original_app = auth_module._firebase_app
    auth_module._firebase_app = None

    # Clear rate limit state so tests start with a clean slate
    _counters.clear()

    with patch("api.config.settings.firebase_auth_enabled", False):
        yield

    auth_module._firebase_app = original_app  # Restore
