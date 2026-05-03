"""
Integration tests for the /chat/stream SSE endpoint.

Tests that:
- The stream endpoint exists and returns 200 (with auth)
- Response content-type is text/event-stream
- SSE events are properly formatted
- 401 returned without auth, 422 with invalid body + auth
"""

import json
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt

from api.config import settings
from api.main import app


def _make_token(phone: str = "+919876543210") -> str:
    """Create a valid local JWT token for test requests."""
    payload = {
        "sub": phone,
        "exp": datetime.now(UTC) + timedelta(minutes=30),
        "iat": datetime.now(UTC),
        "iss": "lokmat-api",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def _auth_headers(phone: str = "+919876543210") -> dict:  # type: ignore[type-arg]
    return {"Authorization": f"Bearer {_make_token(phone)}"}


@pytest.mark.asyncio
async def test_chat_stream_returns_event_stream_content_type() -> None:
    """POST /chat/stream returns text/event-stream content type."""
    payload = {"message": "What is EVM?", "history": [], "session_id": "test-stream-1"}

    async def mock_stream(*args, **kwargs) -> None:  # type: ignore
        yield 'data: {"type": "chunk", "text": "EVM stands for", "model": "flash"}\n\n'
        yield 'data: {"type": "done", "suggestions": [], "model": "flash"}\n\n'

    with patch.object(settings, "firebase_auth_enabled", False):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with patch("api.routers.assistant.classify_intent", return_value="query"), \
                 patch("api.routers.assistant.generate_chat_stream", return_value=mock_stream()):
                response = await client.post("/chat/stream", json=payload, headers=_auth_headers())

    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_chat_stream_emits_valid_sse_events() -> None:
    """POST /chat/stream emits valid SSE events in the response body."""
    payload = {"message": "What is NOTA?", "history": [], "session_id": "test-stream-2"}

    async def mock_stream(*args, **kwargs) -> None:  # type: ignore
        yield 'data: {"type": "chunk", "text": "NOTA is", "model": "flash"}\n\n'
        yield 'data: {"type": "chunk", "text": " None of the Above.", "model": "flash"}\n\n'
        yield 'data: {"type": "done", "suggestions": ["What if NOTA wins?"], "model": "flash"}\n\n'

    with patch.object(settings, "firebase_auth_enabled", False):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with patch("api.routers.assistant.classify_intent", return_value="query"), \
                 patch("api.routers.assistant.generate_chat_stream", return_value=mock_stream()):
                response = await client.post("/chat/stream", json=payload, headers=_auth_headers())

    assert response.status_code == 200
    body = response.text
    lines = [ln for ln in body.split("\n\n") if ln.strip()]
    assert len(lines) >= 2

    for line in lines:
        assert line.strip().startswith("data: ")
        event = json.loads(line.strip()[6:])
        assert "type" in event

    last_event = json.loads(lines[-1].strip()[6:])
    assert last_event["type"] == "done"


@pytest.mark.asyncio
async def test_chat_stream_out_of_scope_handled_via_non_stream() -> None:
    """POST /chat returns 200 with out_of_scope intent for off-topic queries."""
    payload = {
        "message": "What is the best cricket team?",
        "history": [],
        "session_id": "test-oos",
    }
    with patch.object(settings, "firebase_auth_enabled", False):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with patch("api.routers.assistant.classify_intent", return_value="out_of_scope"):
                response = await client.post("/chat", json=payload, headers=_auth_headers())

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "out_of_scope"
    assert "election" in data["message"].lower() or "voting" in data["message"].lower()


@pytest.mark.asyncio
async def test_chat_stream_invalid_body_returns_422() -> None:
    """POST /chat/stream with invalid body returns 422 (schema validation fires after auth)."""
    with patch.object(settings, "firebase_auth_enabled", False):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/chat/stream",
                json={"invalid": "payload"},
                headers=_auth_headers(),
            )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_stream_without_auth_returns_401_or_403() -> None:
    """POST /chat/stream without Bearer token must be rejected."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/chat/stream",
            json={"message": "What is EVM?", "history": []},
        )
    assert response.status_code in (401, 403)
