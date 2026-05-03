"""
LokMat API — Database session management.

Async SQLAlchemy session factory with connection pooling.
Per GEMINI.md: pool_size=10, max_overflow=20.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.config import settings

logger = logging.getLogger(__name__)

# Async engine with connection pooling per GEMINI.md
# SQLite doesn't support pool_size; only apply for PostgreSQL
_engine_kwargs = {
    "echo": settings.debug,
}
if "sqlite" not in settings.database_url:
    _engine_kwargs.update({
        "pool_size": 10,  # type: ignore
        "max_overflow": 20,  # type: ignore
        "pool_pre_ping": True,
    })

engine = create_async_engine(
    settings.database_url,
    **_engine_kwargs,
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:  # type: ignore
    """FastAPI dependency — yields a database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> bool:
    """Check database connectivity. Used by health endpoint."""
    try:
        async with async_session() as session:
            await session.execute(
                __import__("sqlalchemy").text("SELECT 1")
            )
            return True
    except Exception as e:
        logger.error(f"Database connectivity check failed: {e}")
        return False


async def init_db() -> None:
    """Create all tables if they don't exist."""
    from api.models.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")
