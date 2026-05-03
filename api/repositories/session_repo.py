"""
LokMat API — Session repository.

Repository for chat session and message persistence.
Per GEMINI.md: repository pattern for all DB access.
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.models.models import ChatMessage, ChatSession

logger = logging.getLogger(__name__)


class SessionRepository:
    """Repository for ChatSession and ChatMessage CRUD."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_session(self, session_id: str) -> ChatSession | None:
        """Get a chat session with its messages."""
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.id == session_id)
            .options(selectinload(ChatSession.messages))
        )
        return result.scalar_one_or_none()

    async def get_user_sessions(self, user_id: str, limit: int = 20) -> list[ChatSession]:
        """Get recent chat sessions for a user."""
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_session(self, user_id: str, title: str = "Election Query") -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(user_id=user_id, title=title)
        self.db.add(session)
        await self.db.flush()
        logger.info(f"Chat session created: {session.id}")
        return session

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        intent: str = "query",
        tokens_used: int = 0,
        model_used: str = "gemini-2.5-flash",
    ) -> ChatMessage:
        """
        Add a message to a chat session.

        Args:
            session_id: Chat session ID.
            role: 'user' or 'assistant'.
            content: Message text.
            intent: Classified intent.
            tokens_used: Token count for this message.
            model_used: Model identifier used.

        Returns:
            Created ChatMessage instance.
        """
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            intent=intent,
            tokens_used=tokens_used,
            model_used=model_used,
        )
        self.db.add(message)
        await self.db.flush()
        return message

    async def get_recent_messages(
        self,
        session_id: str,
        limit: int = 10,
    ) -> list[ChatMessage]:
        """
        Get the last N messages for context window.

        Per GEMINI.md: rolling window of last 10 turns.
        """
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        messages.reverse()  # Chronological order
        return messages
