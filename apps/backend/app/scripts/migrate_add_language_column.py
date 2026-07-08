"""Idempotent one-time migration: add the ``language`` tenant column.

Each supported language is now treated as its own tenant, with its own master
resume. Existing SQLite databases created before this change are missing the
``language`` column on ``resumes``/``jobs``/``applications`` and still carry
the old globally-unique-master index. This migration is safe to run on every
startup:

- column already present on all three tables → no-op;
- otherwise → add the column (default ``'en'``), backfill existing rows to
  the previously-configured content language (if not already ``en``), then
  swap the single-master index for the per-language composite index.

Run standalone with ``uv run python -m app.scripts.migrate_add_language_column``.
"""

import asyncio
import logging
from typing import Any

from sqlalchemy import text

from app.config_cache import get_content_language
from app.database import Database, db

logger = logging.getLogger(__name__)

_TABLES = ("resumes", "jobs", "applications")


async def _has_language_column(session: Any, table: str) -> bool:
    result = await session.execute(text(f"PRAGMA table_info({table})"))
    columns = {row[1] for row in result.all()}
    return "language" in columns


async def migrate(database: Database | None = None) -> dict[str, Any]:
    """Add the ``language`` column (+ backfill + index swap) if missing.

    Returns a summary dict: ``{"status": ..., ...}``.
    """
    database = database or db

    async with database._session() as session:
        missing = [t for t in _TABLES if not await _has_language_column(session, t)]
        if not missing:
            return {"status": "noop"}

        for table in missing:
            await session.execute(
                text(f"ALTER TABLE {table} ADD COLUMN language TEXT NOT NULL DEFAULT 'en'")
            )

        # Backfill to the previously-configured content language, if it was
        # ever set to something other than the default.
        content_language = get_content_language()
        if content_language and content_language != "en":
            for table in missing:
                await session.execute(
                    text(f"UPDATE {table} SET language = :lang WHERE language = 'en'"),
                    {"lang": content_language},
                )

        if "resumes" in missing:
            await session.execute(text("DROP INDEX IF EXISTS ux_resumes_single_master"))
            await session.execute(
                text(
                    "CREATE UNIQUE INDEX IF NOT EXISTS "
                    "ux_resumes_single_master_per_language "
                    "ON resumes (language, is_master) WHERE is_master = 1"
                )
            )

        await session.commit()

    summary = {"status": "migrated", "tables": missing, "backfilled_language": get_content_language()}
    logger.info("Added language column: %s", summary)
    return summary


def main() -> None:
    """Console entry point for a manual run."""
    logging.basicConfig(level=logging.INFO)
    result = asyncio.run(migrate())
    print(result)


if __name__ == "__main__":
    main()
