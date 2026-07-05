"""Tests for the real SQLAlchemy/SQLite layer (app.database.Database).

Every integration test mocks `db`, so the actual persistence layer was barely
exercised. These run a real SQLite database against a temp file, so CRUD,
master-resume assignment, the jobs ``metadata_json`` round-trip, applications,
and stats are verified end-to-end on the storage.
"""

import pytest

from app.database import Database


@pytest.fixture
async def db(tmp_path):
    database = Database(db_path=tmp_path / "test_db.db")
    yield database
    await database.close()


class TestResumeCrud:
    async def test_create_and_get(self, db):
        created = await db.create_resume(content="# Resume", language="en", filename="r.pdf")
        assert created["resume_id"]
        fetched = await db.get_resume(created["resume_id"])
        assert fetched is not None
        assert fetched["content"] == "# Resume"
        assert fetched["filename"] == "r.pdf"
        assert fetched["language"] == "en"

    async def test_get_missing_returns_none(self, db):
        assert await db.get_resume("does-not-exist") is None

    async def test_list_resumes(self, db):
        await db.create_resume(content="a", language="en")
        await db.create_resume(content="b", language="en")
        assert len(await db.list_resumes(language="en")) == 2

    async def test_list_resumes_scoped_to_tenant(self, db):
        await db.create_resume(content="a", language="en")
        await db.create_resume(content="b", language="fr")
        assert len(await db.list_resumes(language="en")) == 1
        assert len(await db.list_resumes(language="fr")) == 1

    async def test_update_resume_changes_field_and_timestamp(self, db):
        created = await db.create_resume(content="x", language="en")
        updated = await db.update_resume(created["resume_id"], {"title": "New Title"})
        assert updated["title"] == "New Title"
        assert updated["updated_at"] >= created["updated_at"]

    async def test_update_missing_raises(self, db):
        with pytest.raises(ValueError):
            await db.update_resume("missing", {"title": "X"})

    async def test_delete_resume(self, db):
        created = await db.create_resume(content="x", language="en")
        assert await db.delete_resume(created["resume_id"]) is True
        assert await db.get_resume(created["resume_id"]) is None

    async def test_delete_missing_returns_false(self, db):
        assert await db.delete_resume("missing") is False

    async def test_original_markdown_absence_semantics(self, db):
        # Omitted when None (preserve TinyDB behavior); present when supplied.
        without = await db.create_resume(content="x", language="en")
        assert "original_markdown" not in without
        with_md = await db.create_resume(content="x", language="en", original_markdown="# raw")
        fetched = await db.get_resume(with_md["resume_id"])
        assert fetched["original_markdown"] == "# raw"


class TestMasterResume:
    async def test_no_master_initially(self, db):
        assert await db.get_master_resume(language="en") is None

    async def test_set_master_unsets_previous(self, db):
        r1 = await db.create_resume(content="1", language="en")
        r2 = await db.create_resume(content="2", language="en")

        assert await db.set_master_resume(r1["resume_id"], language="en") is True
        assert (await db.get_master_resume(language="en"))["resume_id"] == r1["resume_id"]

        assert await db.set_master_resume(r2["resume_id"], language="en") is True
        master = await db.get_master_resume(language="en")
        assert master["resume_id"] == r2["resume_id"]
        # Only one master at a time.
        assert sum(1 for r in await db.list_resumes(language="en") if r["is_master"]) == 1

    async def test_set_master_missing_returns_false(self, db):
        assert await db.set_master_resume("missing", language="en") is False

    async def test_set_master_wrong_tenant_returns_false(self, db):
        r1 = await db.create_resume(content="1", language="en")
        assert await db.set_master_resume(r1["resume_id"], language="fr") is False

    async def test_atomic_first_upload_becomes_master(self, db):
        created = await db.create_resume_atomic_master(
            content="first", language="en", processing_status="ready"
        )
        assert created["is_master"] is True

    async def test_atomic_second_upload_not_master(self, db):
        await db.create_resume_atomic_master(content="first", language="en", processing_status="ready")
        second = await db.create_resume_atomic_master(
            content="second", language="en", processing_status="ready"
        )
        assert second["is_master"] is False

    async def test_atomic_recovers_when_master_stuck(self, db):
        # Master stuck in "failed" → next upload is promoted to master.
        first = await db.create_resume_atomic_master(
            content="first", language="en", processing_status="failed"
        )
        assert first["is_master"] is True
        second = await db.create_resume_atomic_master(
            content="second", language="en", processing_status="ready"
        )
        assert second["is_master"] is True
        assert (await db.get_master_resume(language="en"))["resume_id"] == second["resume_id"]

    async def test_atomic_master_per_tenant_independent(self, db):
        # Each tenant (language) gets its own master; no cross-tenant clash.
        en_first = await db.create_resume_atomic_master(
            content="en first", language="en", processing_status="ready"
        )
        fr_first = await db.create_resume_atomic_master(
            content="fr first", language="fr", processing_status="ready"
        )
        assert en_first["is_master"] is True
        assert fr_first["is_master"] is True
        assert (await db.get_master_resume(language="en"))["resume_id"] == en_first["resume_id"]
        assert (await db.get_master_resume(language="fr"))["resume_id"] == fr_first["resume_id"]


class TestJobs:
    async def test_create_and_get_job(self, db):
        created = await db.create_job(content="Engineer role", language="en", resume_id="r1")
        fetched = await db.get_job(created["job_id"])
        assert fetched["content"] == "Engineer role"
        assert fetched["resume_id"] == "r1"

    async def test_get_missing_job_returns_none(self, db):
        assert await db.get_job("missing") is None

    async def test_update_job(self, db):
        created = await db.create_job(content="old", language="en")
        updated = await db.update_job(created["job_id"], {"content": "new"})
        assert updated["content"] == "new"

    async def test_update_missing_job_returns_none(self, db):
        assert await db.update_job("missing", {"content": "x"}) is None

    async def test_dynamic_fields_round_trip_as_top_level(self, db):
        """Dynamic pipeline fields must survive write→read as top-level keys.

        This is the highest-risk migration detail: ``/improve/confirm`` rejects
        with 400 if ``preview_hash``/``preview_hashes`` don't round-trip.
        """
        created = await db.create_job(content="jd", language="en")
        await db.update_job(
            created["job_id"],
            {
                "job_keywords": {"required_skills": ["Python", "AWS"]},
                "job_keywords_hash": "deadbeef",
                "preview_hash": "abc123",
                "preview_hashes": {"keywords": "abc123", "nudge": "def456"},
                "preview_prompt_id": "keywords",
                "company": "Acme Corp",
                "role": "Staff Engineer",
            },
        )
        fetched = await db.get_job(created["job_id"])
        # Core fields preserved.
        assert fetched["content"] == "jd"
        # Dynamic fields flattened to the top level.
        assert fetched["preview_hash"] == "abc123"
        assert fetched["preview_hashes"] == {"keywords": "abc123", "nudge": "def456"}
        assert fetched["job_keywords_hash"] == "deadbeef"
        assert fetched["job_keywords"]["required_skills"] == ["Python", "AWS"]
        assert fetched["company"] == "Acme Corp"
        assert fetched["role"] == "Staff Engineer"

    async def test_update_job_merges_metadata(self, db):
        created = await db.create_job(content="jd", language="en")
        await db.update_job(created["job_id"], {"preview_hash": "h1"})
        await db.update_job(created["job_id"], {"company": "Acme"})
        fetched = await db.get_job(created["job_id"])
        # The second update must not wipe the first dynamic field.
        assert fetched["preview_hash"] == "h1"
        assert fetched["company"] == "Acme"


class TestImprovements:
    async def test_create_and_lookup_by_tailored_resume(self, db):
        await db.create_improvement(
            original_resume_id="orig",
            tailored_resume_id="tailored-1",
            job_id="job-1",
            improvements=[{"path": "summary"}],
        )
        found = await db.get_improvement_by_tailored_resume("tailored-1")
        assert found is not None
        assert found["job_id"] == "job-1"

    async def test_lookup_missing_returns_none(self, db):
        assert await db.get_improvement_by_tailored_resume("nope") is None


class TestApplications:
    async def test_create_defaults_and_position(self, db):
        a = await db.create_application(job_id="j1", resume_id="r1", language="en")
        assert a["status"] == "applied"
        assert a["position"] == 0
        assert a["applied_at"] is not None  # applied → stamped
        b = await db.create_application(job_id="j2", resume_id="r2", language="en")
        assert b["position"] == 1  # appended to the column

    async def test_saved_status_has_no_applied_at(self, db):
        a = await db.create_application(job_id="j1", resume_id="r1", language="en", status="saved")
        assert a["applied_at"] is None

    async def test_create_dedupes_on_job_and_resume(self, db):
        a = await db.create_application(job_id="j1", resume_id="r1", language="en")
        again = await db.create_application(job_id="j1", resume_id="r1", language="en")
        assert again["application_id"] == a["application_id"]
        assert len(await db.list_applications(language="en")) == 1

    async def test_move_renumbers_columns(self, db):
        a = await db.create_application(job_id="j1", resume_id="r1", language="en")
        b = await db.create_application(job_id="j2", resume_id="r2", language="en")
        # Move a to the front of "interview".
        moved = await db.update_application(a["application_id"], {"status": "interview", "position": 0})
        assert moved["status"] == "interview"
        assert moved["position"] == 0
        # The "applied" column renumbered: b is now position 0.
        applied = await db.list_applications(language="en", status="applied")
        assert [x["application_id"] for x in applied] == [b["application_id"]]
        assert applied[0]["position"] == 0

    async def test_bulk_update_and_delete(self, db):
        a = await db.create_application(job_id="j1", resume_id="r1", language="en")
        b = await db.create_application(job_id="j2", resume_id="r2", language="en")
        moved = await db.bulk_update_applications([a["application_id"], b["application_id"]], "rejected")
        assert moved == 2
        rejected = await db.list_applications(language="en", status="rejected")
        assert {x["position"] for x in rejected} == {0, 1}
        deleted = await db.bulk_delete_applications([a["application_id"]])
        assert deleted == 1
        remaining = await db.list_applications(language="en", status="rejected")
        assert len(remaining) == 1
        assert remaining[0]["position"] == 0  # renumbered after delete

    async def test_list_applications_scoped_to_tenant(self, db):
        await db.create_application(job_id="j1", resume_id="r1", language="en")
        await db.create_application(job_id="j2", resume_id="r2", language="fr")
        assert len(await db.list_applications(language="en")) == 1
        assert len(await db.list_applications(language="fr")) == 1


class TestApiKeyStore:
    async def test_set_get_delete_ciphertext(self, db):
        db.set_api_key_ciphertext("openai", "ct-openai")
        db.set_api_key_ciphertext("anthropic", "ct-anthropic")
        assert db.get_api_key_ciphertexts() == {"openai": "ct-openai", "anthropic": "ct-anthropic"}
        db.delete_api_key("openai")
        assert db.get_api_key_ciphertexts() == {"anthropic": "ct-anthropic"}
        db.clear_api_keys()
        assert db.get_api_key_ciphertexts() == {}


class TestStatsAndReset:
    async def test_get_stats(self, db):
        await db.create_resume(content="a", language="en")
        await db.set_master_resume((await db.list_resumes(language="en"))[0]["resume_id"], language="en")
        await db.create_job(content="jd", language="en")
        stats = await db.get_stats()
        assert stats["total_resumes"] == 1
        assert stats["total_jobs"] == 1
        assert stats["has_master_resume"] is True

    async def test_reset_database_truncates(self, db, tmp_path, monkeypatch):
        # reset_database also clears settings.data_dir/uploads — isolate it to tmp.
        monkeypatch.setattr("app.database.settings.data_dir", tmp_path)
        await db.create_resume(content="a", language="en")
        await db.create_job(content="jd", language="en")
        await db.create_application(job_id="j1", resume_id="r1", language="en")
        await db.reset_database()
        stats = await db.get_stats()
        assert stats["total_resumes"] == 0
        assert stats["total_jobs"] == 0
        assert stats["has_master_resume"] is False
        # Applications are cleared too (no orphans after a full reset).
        assert await db.list_applications(language="en") == []
