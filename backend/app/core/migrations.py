"""Run Alembic migrations programmatically at application startup.

The app upgrades the schema to the latest revision (`alembic upgrade head`) on
boot, so a fresh `docker compose up` (or any deploy) never runs against an empty
database. Alembic is synchronous, so callers should offload this to a thread
(``asyncio.to_thread``).
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger("fin-auditor")

# app/core/migrations.py -> app/alembic/alembic.ini
_ALEMBIC_INI = Path(__file__).resolve().parent.parent / "alembic" / "alembic.ini"


def run_migrations() -> None:
    """Upgrade the database to the latest Alembic revision (blocking)."""
    from alembic import command
    from alembic.config import Config

    if not _ALEMBIC_INI.exists():
        raise FileNotFoundError(f"Не найден alembic.ini: {_ALEMBIC_INI}")

    cfg = Config(str(_ALEMBIC_INI))
    # Keep the application's logging setup: env.py skips fileConfig(alembic.ini) for us.
    cfg.attributes["configure_logger"] = False
    logger.info("Применение миграций Alembic (upgrade head)...")
    command.upgrade(cfg, "head")
    logger.info("Миграции Alembic применены.")
