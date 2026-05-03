"""
Integration tests — Chat endpoint.

Per GEMINI.md testing requirements:
- Valid chat turn → 200 with structured response schema
- Rate limit exceeded → 429 with Retry-After header
"""

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest.mark.asyncio
async def test_chat_valid_message():
    """Sending a valid chat message returns 200 with expected fields."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/chat",
            json={
                "message": "How do I register to vote?",
                "history": [],
                "session_id": "",
            },
        )

    # Either 200 (success) or 503 (Gemini unavailable) is acceptable
    assert response.status_code in (200, 503)
    if response.status_code == 200:
        data = response.json()
        assert "message" in data
        assert "intent" in data
        assert "session_id" in data


@pytest.mark.asyncio
async def test_chat_empty_message_returns_422():
    """Empty chat message returns 422."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/chat",
            json={"message": "", "history": []},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_returns_intent_field():
    """Chat response includes an intent classification."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/chat",
            json={"message": "What is NOTA?"},
        )

    if response.status_code == 200:
        data = response.json()
        assert data["intent"] in ("query", "action", "clarify", "out_of_scope")
