"""
Integration tests — Health endpoint.

Per GEMINI.md testing requirements:
- /health returns 200 with db, gemini, redis fields
"""

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest.mark.asyncio
async def test_health_returns_200() -> None:
    """Health endpoint returns 200 with service status fields."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "gemini" in data
    assert "version" in data
    assert data["status"] in ("ok", "degraded")


@pytest.mark.asyncio
async def test_health_has_db_field() -> None:
    """Health endpoint includes database status."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/health")

    data = response.json()
    assert "db" in data
    assert data["db"] in ("ok", "error")


@pytest.mark.asyncio
async def test_health_has_redis_field() -> None:
    """Health endpoint includes Redis status."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/health")

    data = response.json()
    assert "redis" in data


@pytest.mark.asyncio
async def test_root_returns_welcome() -> None:
    """Root endpoint returns welcome message."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "services" in data
