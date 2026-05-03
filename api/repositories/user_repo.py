"""
LokMat API — User repository.

Repository pattern for all user DB access.
Per GEMINI.md: No SQL in routers. All DB access through repositories.
"""

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.models import User

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for User CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_phone(self, phone: str) -> User | None:
        """
        Find a user by phone number.

        Args:
            phone: User's phone number with +91 prefix.

        Returns:
            User instance or None if not found.
        """
        result = await self.db.execute(
            select(User).where(User.phone == phone)
        )
        return result.scalar_one_or_none()

    async def get_by_epic(self, epic_no: str) -> User | None:
        """Find a user by EPIC voter ID number."""
        result = await self.db.execute(
            select(User).where(User.epic_no == epic_no)
        )
        return result.scalar_one_or_none()

    async def create(self, phone: str, **kwargs: Any) -> User:
        """
        Create a new user.

        Args:
            phone: Verified phone number.
            **kwargs: Profile fields (full_name, epic_no, etc.).

        Returns:
            Created User instance.
        """
        user = User(phone=phone, **kwargs)
        self.db.add(user)
        await self.db.flush()
        logger.info(f"User created: {phone}")
        return user

    async def update(self, user: User, **kwargs: Any) -> User:
        """
        Update an existing user's profile fields.

        Args:
            user: Existing User instance.
            **kwargs: Fields to update.

        Returns:
            Updated User instance.
        """
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        user.updated_at: datetime = datetime.now(UTC)  # type: ignore[assignment]
        await self.db.flush()
        logger.info(f"User updated: {user.phone}")
        return user

    async def create_or_update(self, phone: str, **kwargs: Any) -> User:
        """
        Create a new user or update existing one.

        Args:
            phone: User's phone number.
            **kwargs: Profile fields.

        Returns:
            User instance (created or updated).
        """
        existing = await self.get_by_phone(phone)
        if existing:
            return await self.update(existing, **kwargs)
        return await self.create(phone=phone, **kwargs)
