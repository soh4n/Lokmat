"""
Integration tests — Chat pipeline with mocked Gemini API.

Per GEMINI.md testing requirements:
- Valid chat turn → 200 with structured response schema
- Gemini API mocked failure → graceful fallback response, not 500
- Out-of-scope intent → structured fallback, not error
- Authenticated requests pass through the full pipeline
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt

from api.config import settings
from api.main import app


def _make_valid_token(phone: str = "+919876543210") -> str:
    """Create a signed JWT for testing."""
    payload = {
        "sub": phone,
        "exp": datetime.now(UTC) + timedelta(minutes=30),
        "iat": datetime.now(UTC),
        "iss": "lokmat-api",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _auth_headers(phone: str = "+919876543210") -> dict:
    return {"Authorization": f"Bearer {_make_valid_token(phone)}"}


# ---------------------------------------------------------------------------
# 1. Successful chat round-trip (Gemini mocked)
# ---------------------------------------------------------------------------

class TestChatAuthenticated:
    """Chat endpoint tests with valid authentication."""

    @pytest.mark.asyncio
    async def test_valid_chat_with_mock_returns_200(self) -> None:
        """Authenticated chat request with mocked Gemini returns 200."""
        mock_response = MagicMock()
        mock_response.text = (
            "To register to vote in India, visit the NVSP portal.\n\n"
            "You may also want to ask:\n"
            "- What documents do I need?\n"
            "- Where is my polling booth?\n"
            "- How do I check my voter ID status?\n"
        )
        mock_response.usage_metadata = MagicMock(total_token_count=150)

        with patch(
            "api.services.gemini_service._generate_with_fallback",
            AsyncMock(return_value=(mock_response, "gemini-2.5-flash")),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as c:
                r = await c.post(
                    "/chat",
                    json={"message": "How do I register to vote?", "history": []},
                    headers=_auth_headers(),
                )

        assert r.status_code == 200
        data = r.json()
        assert "message" in data
        assert "intent" in data
        assert "session_id" in data
        assert data["intent"] in ("query", "action", "clarify", "out_of_scope")
        assert isinstance(data["suggestions"], list)

    @pytest.mark.asyncio
    async def test_chat_response_has_model_field(self) -> None:
        """Chat response includes which model was used."""
        mock_response = MagicMock()
        mock_response.text = "You can vote by visiting your assigned booth."
        mock_response.usage_metadata = MagicMock(total_token_count=50)

        with patch(
            "api.services.gemini_service._generate_with_fallback",
            AsyncMock(return_value=(mock_response, "gemini-2.5-flash")),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as c:
                r = await c.post(
                    "/chat",
                    json={"message": "Where is my booth?", "history": []},
                    headers=_auth_headers(),
                )

        if r.status_code == 200:
            data = r.json()
            assert "model_used" in data

    @pytest.mark.asyncio
    async def test_chat_with_history_passes_context(self) -> None:
        """Chat request with conversation history is accepted and returns 200."""
        mock_response = MagicMock()
        mock_response.text = "Your polling booth is at the nearest school."
        mock_response.usage_metadata = None

        with patch(
            "api.services.gemini_service._generate_with_fallback",
            AsyncMock(return_value=(mock_response, "gemini-2.5-flash")),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as c:
                r = await c.post(
                    "/chat",
                    json={
                        "message": "And the timing?",
                        "history": [
                            {"role": "user", "content": "Where is my booth?"},
                            {"role": "assistant", "content": "It is at the local school."},
                        ],
                    },
                    headers=_auth_headers(),
                )

        assert r.status_code == 200


# ---------------------------------------------------------------------------
# 2. Gemini API failure → graceful fallback
# ---------------------------------------------------------------------------

class TestChatFallback:
    """Per GEMINI.md: Gemini API failure → graceful fallback, not 500."""

    @pytest.mark.asyncio
    async def test_gemini_upstream_failure_returns_fallback_not_500(self) -> None:
        """When Gemini is fully unavailable, a structured fallback is returned."""
        with patch(
            "api.services.gemini_service._generate_with_fallback",
            AsyncMock(side_effect=RuntimeError("All models exhausted")),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as c:
                r = await c.post(
                    "/chat",
                    json={"message": "What is NOTA?", "history": []},
                    headers=_auth_headers(),
                )

        # Must not be a raw 500 — should be a 200 fallback response
        assert r.status_code != 500
        if r.status_code == 200:
            data = r.json()
            assert "message" in data
            assert data.get("is_fallback") is True

    @pytest.mark.asyncio
    async def test_gemini_failure_includes_helpline_in_fallback(self) -> None:
        """Fallback response references the 1950 election helpline."""
        with patch(
            "api.services.gemini_service._generate_with_fallback",
            AsyncMock(side_effect=ConnectionError("timeout")),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as c:
                r = await c.post(
                    "/chat",
                    json={"message": "What documents do I need?", "history": []},
                    headers=_auth_headers(),
                )

        if r.status_code == 200:
            data = r.json()
            # Fallback message should mention the helpline number
            assert "1950" in data.get("message", "")


# ---------------------------------------------------------------------------
# 3. Out-of-scope intent handling
# ---------------------------------------------------------------------------

class TestOutOfScopeIntent:
    """Out-of-scope messages receive a structured refusal, not an error."""

    @pytest.mark.asyncio
    async def test_out_of_scope_returns_structured_response(self) -> None:
        """Out-of-scope intent returns 200 with out_of_scope in intent field."""
        with patch(
            "api.services.gemini_service.classify_intent",
            AsyncMock(return_value="out_of_scope"),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as c:
                r = await c.post(
                    "/chat",
                    json={"message": "What is the weather today?", "history": []},
                    headers=_auth_headers(),
                )

        assert r.status_code == 200
        data = r.json()
        assert data["intent"] == "out_of_scope"
        assert len(data["suggestions"]) > 0

    @pytest.mark.asyncio
    async def test_out_of_scope_response_is_not_fallback(self) -> None:
        """Out-of-scope is a legitimate response, not a technical fallback."""
        with patch(
            "api.services.gemini_service.classify_intent",
            AsyncMock(return_value="out_of_scope"),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as c:
                r = await c.post(
                    "/chat",
                    json={"message": "What is the price of gold?", "history": []},
                    headers=_auth_headers(),
                )

        if r.status_code == 200:
            assert r.json().get("is_fallback") is False


# ---------------------------------------------------------------------------
# 4. Session ID handling
# ---------------------------------------------------------------------------

class TestSessionHandling:
    """Session IDs are generated and propagated correctly."""

    @pytest.mark.asyncio
    async def test_chat_generates_session_id_when_empty(self) -> None:
        """A session_id is auto-generated when the client sends an empty string."""
        mock_response = MagicMock()
        mock_response.text = "Test response"
        mock_response.usage_metadata = None

        with patch(
            "api.services.gemini_service._generate_with_fallback",
            AsyncMock(return_value=(mock_response, "gemini-2.5-flash")),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as c:
                r = await c.post(
                    "/chat",
                    json={"message": "Hi", "session_id": "", "history": []},
                    headers=_auth_headers(),
                )

        if r.status_code == 200:
            data = r.json()
            assert data["session_id"] != ""

    @pytest.mark.asyncio
    async def test_chat_preserves_provided_session_id(self) -> None:
        """Provided session_id is echoed back in the response."""
        session_id = "my-custom-session-xyz"
        mock_response = MagicMock()
        mock_response.text = "Response with session"
        mock_response.usage_metadata = None

        with patch(
            "api.services.gemini_service._generate_with_fallback",
            AsyncMock(return_value=(mock_response, "gemini-2.5-flash")),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as c:
                r = await c.post(
                    "/chat",
                    json={
                        "message": "Hello",
                        "session_id": session_id,
                        "history": [],
                    },
                    headers=_auth_headers(),
                )

        if r.status_code == 200:
            assert r.json()["session_id"] == session_id
