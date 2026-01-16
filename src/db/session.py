"""Database session management for async SQLAlchemy."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

# Default database URL (SQLite for development)
DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///./hotdeal.db"


def get_database_url() -> str:
    """Get database URL from environment variable or use default.

    Environment variable: DATABASE_URL

    Examples:
        - SQLite: sqlite+aiosqlite:///./hotdeal.db
        - PostgreSQL: postgresql+asyncpg://user:pass@localhost/hotdeal
        - MariaDB: mysql+aiomysql://user:pass@localhost/hotdeal
    """
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def get_async_engine(database_url: str | None = None) -> AsyncEngine:
    """Create an async SQLAlchemy engine.

    Args:
        database_url: Database connection URL. If None, uses get_database_url().

    Returns:
        AsyncEngine instance
    """
    url = database_url or get_database_url()

    # SQLite specific settings
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_async_engine(
        url,
        echo=os.getenv("DATABASE_ECHO", "").lower() == "true",
        connect_args=connect_args,
    )


def get_async_session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create an async session maker.

    Args:
        engine: AsyncEngine instance

    Returns:
        async_sessionmaker instance
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


@asynccontextmanager
async def get_async_session(engine: AsyncEngine | None = None) -> AsyncGenerator[AsyncSession, None]:
    """Context manager for async database sessions.

    Args:
        engine: AsyncEngine instance. If None, creates a new engine.

    Yields:
        AsyncSession instance

    Example:
        async with get_async_session() as session:
            result = await session.execute(select(Article))
            articles = result.scalars().all()
    """
    if engine is None:
        engine = get_async_engine()

    session_maker = get_async_session_maker(engine)
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Global engine instance (lazy initialization)
_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    """Get or create the global async engine instance."""
    global _engine
    if _engine is None:
        _engine = get_async_engine()
    return _engine


async def init_db(engine: AsyncEngine | None = None) -> None:
    """Initialize database tables.

    Args:
        engine: AsyncEngine instance. If None, uses global engine.

    Note:
        This should only be used for development/testing.
        Use Alembic migrations for production.
    """
    from .models import Base

    if engine is None:
        engine = get_engine()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close the global database engine."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
