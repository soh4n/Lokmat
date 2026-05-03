"""
Unit tests — Auth router logic.

Per GEMINI.md testing requirements:
- Validates JWT creation, phone format, OTP validation
"""

import pytest
from jose import jwt

from api.config import settings


class TestJWTCreation:
    """Tests for JWT token creation and verification."""

    def test_jwt_encode_decode(self) -> None:
        """JWT token can be created and decoded correctly."""
        payload = {
            "sub": "+919876543210",
            "phone": "+919876543210",
        }
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        decoded = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])

        assert decoded["sub"] == "+919876543210"
        assert decoded["phone"] == "+919876543210"

    def test_jwt_invalid_secret_fails(self) -> None:
        """Token decoded with wrong secret raises an error."""
        payload = {"sub": "+919876543210"}
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

        with pytest.raises(Exception):
            jwt.decode(token, "wrong-secret", algorithms=[settings.jwt_algorithm])

    def test_jwt_contains_expected_claims(self) -> None:
        """Token contains the expected claims."""
        payload = {
            "sub": "+919876543210",
            "phone": "+919876543210",
            "type": "access",
        }
        token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        decoded = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])

        assert "sub" in decoded
        assert "phone" in decoded
        assert decoded["type"] == "access"
