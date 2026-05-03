from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Import all models to get definition coverage
from api.models.models import ChatSession, User
from api.repositories.session_repo import SessionRepository
from api.repositories.user_repo import UserRepository
from api.services.audit_service import audit
from api.services.cache_service import CacheService
from api.utils.auth import create_access_token, verify_token


class _Result:
    def __init__(self, scalar: object) -> None:
        self._scalar = scalar

    def scalar_one_or_none(self) -> object:
        return self._scalar


class _FakeDb:
    def __init__(self, scalar: object) -> None:
        self._result = _Result(scalar)

    async def execute(self, statement: object) -> _Result:
        self.statement = statement
        return self._result


@pytest.mark.asyncio
async def test_session_repository() -> None:
    mock_db = _FakeDb(ChatSession(id="123"))
    repo = SessionRepository(mock_db)
    res = await repo.get_session("123")
    assert res is not None

@pytest.mark.asyncio
async def test_user_repository() -> None:
    mock_db = _FakeDb(User(phone="9999"))
    repo = UserRepository(mock_db)
    res = await repo.get_by_phone("9999")
    assert res is not None

@pytest.mark.asyncio
async def test_audit_service() -> None:
    with patch("api.services.audit_service.logger") as mock_logger:
        audit.log_chat_event(
            user_phone="u1",
            intent="query",
            model="flash",
            latency_ms=100,
            tokens=50,
            status="ok"
        )
        mock_logger.info.assert_called()

@pytest.mark.asyncio
async def test_cache_service() -> None:
    cache = CacheService(redis_url=None)
    await cache.set_cached_response("hello", "world")
    res = await cache.get_cached_response("hello")
    assert res == "world"

def test_auth_utils() -> None:
    token, exp = create_access_token("+919876543210")
    assert token is not None
    # Assuming local mode is tested
    with patch("api.utils.auth.settings.firebase_auth_enabled", False):
        user = verify_token(token)
        assert user == "+919876543210"

@pytest.mark.asyncio
async def test_rate_limit() -> None:
    from fastapi import Request

    from api.utils.rate_limit import RateLimitMiddleware
    req = MagicMock(spec=Request)
    req.url.path = "/health"
    limiter = RateLimitMiddleware(app=MagicMock())
    async def mock_next(r: Any) -> Any: return None
    await limiter.dispatch(req, mock_next)
