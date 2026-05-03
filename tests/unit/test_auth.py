"""
Unit tests — auth utility (token creation, verification, masking).

Per GEMINI.md testing requirements:
- JWT tokens created with correct claims and TTL
- Expired tokens are rejected
- Missing 'sub' claim returns None
- Tampered signature returns None
- Phone masking produces safe log-friendly output
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from jose import jwt

from api.config import settings
from api.utils.auth import create_access_token, verify_token


class TestCreateAccessToken:
    """Tests for JWT creation helper."""

    def test_creates_token_with_sub_claim(self) -> None:
        """Token contains the phone number as the 'sub' claim."""
        token, _ = create_access_token("+919876543210")
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == "+919876543210"

    def test_creates_token_with_iss_claim(self) -> None:
        """Token contains the 'lokmat-api' issuer claim."""
        token, _ = create_access_token("+919876543210")
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        assert payload.get("iss") == "lokmat-api"

    def test_returns_expiry_seconds(self) -> None:
        """Returns the expiry duration in seconds."""
        _, expiry = create_access_token("+919876543210")
        assert expiry == settings.jwt_expiry_minutes * 60

    def test_token_expires_after_configured_window(self) -> None:
        """Token's exp claim is approximately jwt_expiry_minutes from now."""
        token, _ = create_access_token("+919876543210")
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        now = datetime.now(UTC).timestamp()
        expected_exp = now + settings.jwt_expiry_minutes * 60
        # Allow 5s tolerance for test execution time
        assert abs(payload["exp"] - expected_exp) < 5

    def test_different_phones_produce_different_tokens(self) -> None:
        """Each phone number produces a distinct token."""
        t1, _ = create_access_token("+919876543210")
        t2, _ = create_access_token("+919876543211")
        assert t1 != t2


class TestVerifyToken:
    """Tests for the token verification path."""

    def test_valid_token_returns_phone(self) -> None:
        """A freshly created token verifies successfully."""
        with patch.object(settings, "firebase_auth_enabled", False):
            token, _ = create_access_token("+919876543210")
            result = verify_token(token)
        assert result == "+919876543210"

    def test_expired_token_returns_none(self) -> None:
        """An expired JWT returns None rather than raising."""
        with patch.object(settings, "firebase_auth_enabled", False):
            payload = {
                "sub": "+919876543210",
                "exp": datetime.now(UTC) - timedelta(seconds=1),
                "iat": datetime.now(UTC) - timedelta(minutes=30),
                "iss": "lokmat-api",
            }
            expired_token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
            result = verify_token(expired_token)
        assert result is None

    def test_tampered_signature_returns_none(self) -> None:
        """Tokens with tampered signature return None."""
        with patch.object(settings, "firebase_auth_enabled", False):
            token, _ = create_access_token("+919876543210")
            # Corrupt the signature part
            parts = token.split(".")
            bad_token = ".".join(parts[:2] + ["invalidsignature"])
            result = verify_token(bad_token)
        assert result is None

    def test_wrong_secret_returns_none(self) -> None:
        """Token signed with wrong secret returns None."""
        with patch.object(settings, "firebase_auth_enabled", False):
            payload = {
                "sub": "+919876543210",
                "exp": datetime.now(UTC) + timedelta(hours=1),
            }
            bad_token = jwt.encode(payload, "wrong-secret", algorithm="HS256")
            result = verify_token(bad_token)
        assert result is None

    def test_missing_sub_claim_returns_none(self) -> None:
        """Token without 'sub' claim returns None."""
        with patch.object(settings, "firebase_auth_enabled", False):
            payload = {
                "exp": datetime.now(UTC) + timedelta(hours=1),
                "iss": "lokmat-api",
            }
            token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
            result = verify_token(token)
        assert result is None

    def test_empty_string_token_returns_none(self) -> None:
        """Empty string token returns None without raising."""
        with patch.object(settings, "firebase_auth_enabled", False):
            result = verify_token("")
        assert result is None

    def test_garbage_token_returns_none(self) -> None:
        """Completely invalid string returns None without raising."""
        with patch.object(settings, "firebase_auth_enabled", False):
            result = verify_token("not.a.token")
        assert result is None


class TestPhoneMasking:
    """Tests for the phone masking helper in the auth router."""

    def test_masking_hides_middle_digits(self) -> None:
        """Middle digits of phone number are replaced with X characters."""
        from api.routers.auth import _mask_phone
        masked = _mask_phone("+919876543210")
        assert masked.endswith("3210")
        assert "X" in masked
        assert "9876" not in masked

    def test_short_phone_is_fully_masked(self) -> None:
        """Phone numbers with 4 or fewer characters become ****."""
        from api.routers.auth import _mask_phone
        assert _mask_phone("1234") == "****"
        assert _mask_phone("12") == "****"

    def test_standard_indian_number_masked_correctly(self) -> None:
        """Standard +91 format phone produces safe masked output."""
        from api.routers.auth import _mask_phone
        result = _mask_phone("+919876543210")
        # Must retain the last 4 digits
        assert result.endswith("3210")
        # Must not contain the full number
        assert result != "+919876543210"
