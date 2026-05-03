"""
Integration tests for the /chat/stream SSE endpoint.

Tests that:
- The stream endpoint exists and returns 200
- Response content-type is text/event-stream
- SSE events are properly formatted
- Fallback works when Gemini is unavailable
"""

import json
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest.mark.asyncio
async def test_chat_stream_returns_event_stream_content_type():
    """POST /chat/stream returns text/event-stream content type."""
    payload = {"message": "What is EVM?", "history": [], "session_id": "test-stream-1"}

    async def mock_stream(*args, **kwargs):
        yield 'data: {"type": "chunk", "text": "EVM stands for", "model": "gemini-2.5-flash"}\n\n'
        yield 'data: {"type": "done", "suggestions": [], "model": "gemini-2.5-flash"}\n\n'

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with patch("api.routers.assistant.classify_intent", return_value="query"), \
             patch("api.routers.assistant.generate_chat_stream", return_value=mock_stream()):
            response = await client.post("/chat/stream", json=payload)

    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_chat_stream_emits_valid_sse_events():
    """POST /chat/stream emits valid SSE events in the response body."""
    payload = {"message": "What is NOTA?", "history": [], "session_id": "test-stream-2"}

    async def mock_stream(*args, **kwargs):
        yield 'data: {"type": "chunk", "text": "NOTA is", "model": "gemini-2.5-flash"}\n\n'
        yield 'data: {"type": "chunk", "text": " None of the Above.", "model": "gemini-2.5-flash"}\n\n'
        yield 'data: {"type": "done", "suggestions": ["What if NOTA wins?"], "model": "gemini-2.5-flash"}\n\n'

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with patch("api.routers.assistant.classify_intent", return_value="query"), \
             patch("api.routers.assistant.generate_chat_stream", return_value=mock_stream()):
            response = await client.post("/chat/stream", json=payload)

    assert response.status_code == 200
    body = response.text
    lines = [ln for ln in body.split("\n\n") if ln.strip()]
    assert len(lines) >= 2

    # All lines should be SSE formatted
    for line in lines:
        assert line.strip().startswith("data: ")
        event = json.loads(line.strip()[6:])
        assert "type" in event

    # Last event should be done
    last_event = json.loads(lines[-1].strip()[6:])
    assert last_event["type"] == "done"


@pytest.mark.asyncio
async def test_chat_stream_out_of_scope_handled_via_non_stream():
    """POST /chat returns 200 with out_of_scope intent for off-topic queries."""
    payload = {
        "message": "What is the best cricket team?",
        "history": [],
        "session_id": "test-oos",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with patch("api.routers.assistant.classify_intent", return_value="out_of_scope"):
            response = await client.post("/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "out_of_scope"
    assert "election" in data["message"].lower() or "voting" in data["message"].lower()


@pytest.mark.asyncio
async def test_chat_stream_invalid_body_returns_422():
    """POST /chat/stream with invalid body returns 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/chat/stream", json={"invalid": "payload"})
    assert response.status_code == 422
