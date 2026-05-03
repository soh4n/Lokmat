import pytest
from typing import Any
from unittest.mock import AsyncMock, patch, MagicMock

# Import all models to get definition coverage
import api.models.models
from api.models.models import Base, User, ChatSession, ChatMessage, AuditLog
from api.services.audit_service import audit
from api.repositories.session_repo import SessionRepository
from api.repositories.user_repo import UserRepository
from api.services.cache_service import CacheService
from api.utils.auth import create_access_token, verify_token, _verify_local_jwt

@pytest.mark.asyncio
async def test_session_repository() -> None:
    mock_db = AsyncMock()
    repo = SessionRepository(mock_db)
    mock_db.execute.return_value.scalars.return_value.first.return_value = ChatSession(id="123")
    res = await repo.get_session("123")
    assert res is not None

@pytest.mark.asyncio
async def test_user_repository() -> None:
    mock_db = AsyncMock()
    repo = UserRepository(mock_db)
    mock_db.execute.return_value.scalars.return_value.first.return_value = User(phone="9999")
    res = await repo.get_by_phone("9999")
    assert res is not None

@pytest.mark.asyncio
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
    from api.utils.rate_limit import RateLimitMiddleware
    from fastapi import Request
    req = MagicMock(spec=Request)
    req.url.path = "/health"
    limiter = RateLimitMiddleware(app=MagicMock())
    async def mock_next(r: Any) -> Any: return None
    await limiter.dispatch(req, mock_next)
