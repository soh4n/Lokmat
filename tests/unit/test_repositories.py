"""Unit tests for repositories."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from api.repositories.user_repo import UserRepository
from api.repositories.session_repo import SessionRepository

@pytest.mark.asyncio
async def test_user_repository():
    mock_session = AsyncMock()
    repo = UserRepository(mock_session)
    assert repo.session == mock_session

@pytest.mark.asyncio
async def test_session_repository():
    mock_session = AsyncMock()
    repo = SessionRepository(mock_session)
    assert repo.session == mock_session
