"""Shared pytest fixtures."""
import asyncio
import os

import pytest

# Ensure test settings don't touch real DB / Redis
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("DATABASE_URL_SYNC", "sqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("CELERY_BROKER_URL", "memory://")
os.environ.setdefault("CELERY_RESULT_BACKEND", "cache+memory://")
os.environ.setdefault("SECRET_KEY", "test-secret")
# Don't run Alembic migrations (Postgres-specific) against the sqlite test DB.
os.environ.setdefault("RUN_MIGRATIONS_ON_STARTUP", "false")


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
