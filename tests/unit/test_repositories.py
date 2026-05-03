"""Unit tests for repositories."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from api.repositories.session_repo import SessionRepository
from api.repositories.user_repo import UserRepository


@pytest.mark.asyncio
async def test_user_repository() -> None:
    mock_session = AsyncMock()
    repo = UserRepository(mock_session)
    assert repo.db == mock_session

@pytest.mark.asyncio
async def test_session_repository() -> None:
    mock_session = AsyncMock()
    repo = SessionRepository(mock_session)
    assert repo.db == mock_session
