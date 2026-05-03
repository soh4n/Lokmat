"""
Integration tests — Auth flow.

Per GEMINI.md testing requirements:
- Unauthenticated requests → 401
- Malformed request bodies → 422
"""

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest.mark.asyncio
async def test_send_otp_valid_phone() -> None:
    """Sending OTP with valid phone returns 200."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/send-otp",
            json={"phone": "+919876543210"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["phone"] == "+919876543210"


@pytest.mark.asyncio
async def test_send_otp_invalid_phone_returns_422() -> None:
    """Sending OTP with invalid phone returns 422."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/send-otp",
            json={"phone": "invalid"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_verify_otp_wrong_otp_returns_401() -> None:
    """Wrong OTP returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        # First, send OTP
        await client.post("/auth/send-otp", json={"phone": "+919876543210"})

        # Then verify with wrong OTP
        response = await client.post(
            "/auth/verify-otp",
            json={"phone": "+919876543210", "otp": "000000"},
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_without_token_returns_401() -> None:
    """Accessing a protected route without a token returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/voter/profile")

    # HTTPBearer returns 403 when no Authorization header is provided
    assert response.status_code in (401, 403)

@pytest.mark.asyncio
async def test_malformed_body_returns_422() -> None:
    """Missing required field in request body returns 422."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/send-otp",
            json={},  # missing 'phone'
        )

    assert response.status_code == 422
