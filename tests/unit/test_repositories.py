"""Unit tests for repositories."""
from unittest.mock import AsyncMock

import pytest

from api.models.models import ChatMessage, ChatSession, User
from api.repositories.session_repo import SessionRepository
from api.repositories.user_repo import UserRepository


class _ScalarList:
    def __init__(self, values):
        self._values = values

    def all(self):
        return self._values


class _Result:
    def __init__(self, scalar=None, values=None):
        self._scalar = scalar
        self._values = values or []

    def scalar_one_or_none(self):
        return self._scalar

    def scalars(self):
        return _ScalarList(self._values)


class _FakeDb:
    def __init__(self, result):
        self.result = result
        self.added = []
        self.flushed = False

    async def execute(self, statement):
        self.statement = statement
        return self.result

    def add(self, item):
        self.added.append(item)

    async def flush(self):
        self.flushed = True


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


@pytest.mark.asyncio
async def test_user_repository_queries_and_mutations() -> None:
    user = User(phone="+919999999999", epic_no="ABC1234567")
    db = _FakeDb(_Result(scalar=user))
    repo = UserRepository(db)  # type: ignore[arg-type]

    assert await repo.get_by_phone(user.phone) is user
    assert await repo.get_by_epic(user.epic_no) is user

    created = await repo.create("+918888888888", full_name="Test User")
    assert created.phone == "+918888888888"
    assert created.full_name == "Test User"
    assert db.added[-1] is created
    assert db.flushed is True

    updated = await repo.update(created, full_name="Updated User", unknown="ignored")
    assert updated.full_name == "Updated User"
    assert not hasattr(updated, "unknown")


@pytest.mark.asyncio
async def test_user_repository_create_or_update_branches() -> None:
    existing = User(phone="+917777777777", full_name="Old")
    repo = UserRepository(_FakeDb(_Result(scalar=existing)))  # type: ignore[arg-type]
    updated = await repo.create_or_update(existing.phone, full_name="New")
    assert updated is existing
    assert updated.full_name == "New"

    db = _FakeDb(_Result(scalar=None))
    repo = UserRepository(db)  # type: ignore[arg-type]
    created = await repo.create_or_update("+916666666666", full_name="Created")
    assert created.phone == "+916666666666"
    assert db.added[-1] is created


@pytest.mark.asyncio
async def test_session_repository_queries_and_mutations() -> None:
    session = ChatSession(id="session-1", user_id="+919999999999", title="Election Query")
    message = ChatMessage(session_id="session-1", role="user", content="What is NOTA?")
    db = _FakeDb(_Result(scalar=session, values=[session]))
    repo = SessionRepository(db)  # type: ignore[arg-type]

    assert await repo.get_session("session-1") is session
    assert await repo.get_user_sessions("+919999999999", limit=5) == [session]

    created_session = await repo.create_session("+918888888888", title="Booth lookup")
    assert created_session.user_id == "+918888888888"
    assert created_session.title == "Booth lookup"
    assert db.added[-1] is created_session

    created_message = await repo.add_message(
        session_id="session-1",
        role="assistant",
        content="NOTA means None of the Above.",
        intent="query",
        tokens_used=12,
        model_used="gemini-test",
    )
    assert created_message.session_id == "session-1"
    assert created_message.tokens_used == 12
    assert db.added[-1] is created_message

    db.result = _Result(values=[message])
    assert await repo.get_recent_messages("session-1", limit=10) == [message]
