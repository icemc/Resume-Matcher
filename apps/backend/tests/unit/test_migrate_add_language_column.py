"""Tests for the idempotent ``language`` column migration.

Builds a pre-migration SQLite file by hand (old schema: no ``language``
column, old globally-unique-master index) so the migration's ALTER/backfill/
index-swap logic runs against real "before" state, then verifies the
already-migrated case is a true no-op.
"""

import sqlite3

import pytest
from sqlalchemy import text

from app.database import Database
from app.scripts.migrate_add_language_column import migrate


def _create_pre_migration_schema(db_path) -> None:
    """Create resumes/jobs/applications without ``language`` (old shape)."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE resumes (
                resume_id TEXT PRIMARY KEY,
                content TEXT,
                content_type TEXT,
                filename TEXT,
                is_master BOOLEAN,
                parent_id TEXT,
                processed_data TEXT,
                processing_status TEXT,
                cover_letter TEXT,
                outreach_message TEXT,
                title TEXT,
                original_markdown TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )
        conn.execute(
            "CREATE UNIQUE INDEX ux_resumes_single_master "
            "ON resumes (is_master) WHERE is_master = 1"
        )
        conn.execute(
            """
            CREATE TABLE jobs (
                job_id TEXT PRIMARY KEY,
                content TEXT,
                resume_id TEXT,
                created_at TEXT,
                metadata_json TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE applications (
                application_id TEXT PRIMARY KEY,
                job_id TEXT,
                resume_id TEXT,
                master_resume_id TEXT,
                status TEXT,
                company TEXT,
                role TEXT,
                applied_at TEXT,
                notes TEXT,
                position INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )
        conn.execute(
            "INSERT INTO resumes (resume_id, content, is_master, created_at, updated_at) "
            "VALUES ('r1', 'old resume', 1, 't', 't')"
        )
        conn.commit()
    finally:
        conn.close()


@pytest.fixture
def pre_migration_db_path(tmp_path):
    db_path = tmp_path / "pre_migration.db"
    _create_pre_migration_schema(db_path)
    return db_path


async def _table_columns(database: Database, table: str) -> set[str]:
    async with database._session() as session:
        result = await session.execute(text(f"PRAGMA table_info({table})"))
        return {row[1] for row in result.all()}


async def _index_names(database: Database, table: str) -> set[str]:
    async with database._session() as session:
        result = await session.execute(text(f"PRAGMA index_list({table})"))
        return {row[1] for row in result.all()}


class TestMigrateAddLanguageColumn:
    async def test_adds_language_column_and_backfills_default(
        self, pre_migration_db_path, monkeypatch
    ):
        monkeypatch.setattr(
            "app.scripts.migrate_add_language_column.get_content_language", lambda: "en"
        )
        database = Database(db_path=pre_migration_db_path)
        try:
            result = await migrate(database)
            assert result["status"] == "migrated"
            assert set(result["tables"]) == {"resumes", "jobs", "applications"}

            for table in ("resumes", "jobs", "applications"):
                assert "language" in await _table_columns(database, table)

            async with database._session() as session:
                row = (
                    await session.execute(text("SELECT language FROM resumes WHERE resume_id = 'r1'"))
                ).first()
                assert row[0] == "en"
        finally:
            await database.close()

    async def test_swaps_single_master_index_for_per_language_index(self, pre_migration_db_path):
        database = Database(db_path=pre_migration_db_path)
        try:
            await migrate(database)
            indexes = await _index_names(database, "resumes")
            assert "ux_resumes_single_master" not in indexes
            assert "ux_resumes_single_master_per_language" in indexes
        finally:
            await database.close()

    async def test_backfills_non_default_content_language(self, pre_migration_db_path, monkeypatch):
        monkeypatch.setattr(
            "app.scripts.migrate_add_language_column.get_content_language", lambda: "fr"
        )
        database = Database(db_path=pre_migration_db_path)
        try:
            result = await migrate(database)
            assert result["backfilled_language"] == "fr"
            async with database._session() as session:
                row = (
                    await session.execute(text("SELECT language FROM resumes WHERE resume_id = 'r1'"))
                ).first()
                assert row[0] == "fr"
        finally:
            await database.close()

    async def test_rerun_is_true_noop(self, pre_migration_db_path):
        database = Database(db_path=pre_migration_db_path)
        try:
            first = await migrate(database)
            assert first["status"] == "migrated"
            second = await migrate(database)
            assert second == {"status": "noop"}
        finally:
            await database.close()

    async def test_fresh_database_is_already_migrated_noop(self, tmp_path):
        # A brand-new Database (created via the current models, which already
        # define ``language``) should never need the migration.
        database = Database(db_path=tmp_path / "fresh.db")
        try:
            result = await migrate(database)
            assert result == {"status": "noop"}
        finally:
            await database.close()
