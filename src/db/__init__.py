"""Database layer for user-hotdeal-bot API."""

from .models import ApiKey, Article, Base, GuestRateLimit, Settings
from .repository import ApiKeyRepository, ArticleRepository, GuestRateLimitRepository, SettingsRepository
from .session import close_db, get_async_engine, get_async_session, get_database_url, get_engine, init_db

__all__ = [
    # Models
    "Base",
    "Article",
    "ApiKey",
    "GuestRateLimit",
    "Settings",
    # Session
    "get_database_url",
    "get_async_engine",
    "get_async_session",
    "get_engine",
    "init_db",
    "close_db",
    # Repository
    "ArticleRepository",
    "ApiKeyRepository",
    "GuestRateLimitRepository",
    "SettingsRepository",
]
