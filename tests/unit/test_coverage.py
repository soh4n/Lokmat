import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# Import all models to get definition coverage
import api.models.models
from api.models.models import Base, User, Session, Message, AuditLog
from api.repositories.session_repo import SessionRepository
from api.repositories.user_repo import UserRepository
from api.services.audit_service import audit_service, AuditLogMessage
from api.services.cache_service import CacheService
from api.utils.auth import create_access_token, verify_token, _verify_local_jwt

@pytest.mark.asyncio
async def test_session_repository():
    mock_db = AsyncMock()
    repo = SessionRepository(mock_db)
    mock_db.execute.return_value.scalars.return_value.first.return_value = Session(id="123")
    res = await repo.get_session("123", "user1")
    assert res is not None

@pytest.mark.asyncio
async def test_user_repository():
    mock_db = AsyncMock()
    repo = UserRepository(mock_db)
    mock_db.execute.return_value.scalars.return_value.first.return_value = User(phone="9999")
    res = await repo.get_user_by_phone("9999")
    assert res is not None

@pytest.mark.asyncio
async def test_audit_service():
    msg = AuditLogMessage(
        user_id="u1",
        session_id="s1",
        intent="query",
        model_used="flash",
        latency_ms=100,
        tokens_used=50,
        status="ok"
    )
    with patch("api.services.audit_service.logger") as mock_logger:
        await audit_service.log_event(msg)
        mock_logger.info.assert_called()

@pytest.mark.asyncio
async def test_cache_service():
    cache = CacheService(redis_url=None)
    await cache.set_cached_response("hello", "world")
    res = await cache.get_cached_response("hello")
    assert res == "world"

def test_auth_utils():
    token, exp = create_access_token("+919876543210")
    assert token is not None
    # Assuming local mode is tested
    with patch("api.utils.auth.settings.firebase_auth_enabled", False):
        user = verify_token(token)
        assert user == "+919876543210"

@pytest.mark.asyncio
async def test_rate_limit():
    from api.utils.rate_limit import RateLimiter
    from fastapi import Request
    req = MagicMock(spec=Request)
    req.state.user_id = "test"
    limiter = RateLimiter(60, 60)
    with patch("api.utils.rate_limit.cache_service.check_rate_limit", return_value=True):
        await limiter(req)
