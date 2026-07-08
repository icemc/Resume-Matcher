"""Cross-tenant isolation through the real routers (language = tenant).

Complements the DB-layer tenant tests in ``tests/unit/test_database.py`` by
proving isolation holds through the actual HTTP surface: resumes, jobs, and
the application tracker must never leak data across a ``language`` boundary,
and an unsupported tenant must be rejected before touching the database.
"""

import asyncio
import copy
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def _new_client() -> AsyncClient:
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


async def _upload_resume(sample_resume: dict, language: str) -> dict:
    """Upload a fake PDF for the given tenant; return the parsed JSON body."""
    markdown = "# Jane Doe\nSenior Backend Engineer\njane@example.com\n"
    with (
        patch(
            "app.routers.resumes.parse_document",
            new_callable=AsyncMock,
            return_value=markdown,
        ),
        patch(
            "app.routers.resumes.parse_resume_to_json",
            new_callable=AsyncMock,
            return_value=copy.deepcopy(sample_resume),
        ),
    ):
        async with _new_client() as client:
            resp = await client.post(
                "/api/v1/resumes/upload",
                files={"file": ("resume.pdf", b"%PDF-1.4 fake", "application/pdf")},
                data={"language": language},
            )
    assert resp.status_code == 200, resp.text
    return resp.json()


class TestMasterPerTenant:
    async def test_each_tenant_gets_its_own_master_without_clash(
        self, isolated_db, sample_resume
    ):
        en_body = await _upload_resume(sample_resume, "en")
        fr_body = await _upload_resume(sample_resume, "fr")

        en_master = await isolated_db.get_master_resume(language="en")
        fr_master = await isolated_db.get_master_resume(language="fr")

        assert en_master is not None and en_master["resume_id"] == en_body["resume_id"]
        assert fr_master is not None and fr_master["resume_id"] == fr_body["resume_id"]
        assert en_master["resume_id"] != fr_master["resume_id"]

    async def test_concurrent_same_language_uploads_yield_exactly_one_master(
        self, isolated_db, sample_resume
    ):
        results = await asyncio.gather(
            *(_upload_resume(sample_resume, "en") for _ in range(5))
        )
        resume_ids = {body["resume_id"] for body in results}
        assert len(resume_ids) == 5  # every upload persisted its own resume

        all_resumes = await isolated_db.list_resumes(language="en")
        masters = [r for r in all_resumes if r["is_master"]]
        assert len(masters) == 1


class TestListScoping:
    async def test_list_resumes_by_language_excludes_other_tenants(
        self, isolated_db, sample_resume
    ):
        await _upload_resume(sample_resume, "en")
        await _upload_resume(sample_resume, "fr")

        async with _new_client() as client:
            resp = await client.get(
                "/api/v1/resumes/list", params={"include_master": True, "language": "en"}
            )
        assert resp.status_code == 200
        listed = resp.json()["data"]
        assert len(listed) == 1

        async with _new_client() as client:
            resp = await client.get(
                "/api/v1/resumes/list", params={"include_master": True, "language": "fr"}
            )
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 1


class TestCrossTenantFetch404:
    async def test_fetch_resume_from_wrong_tenant_returns_404(
        self, isolated_db, sample_resume
    ):
        fr_body = await _upload_resume(sample_resume, "fr")

        async with _new_client() as client:
            resp = await client.get(
                "/api/v1/resumes",
                params={"resume_id": fr_body["resume_id"], "language": "en"},
            )
        assert resp.status_code == 404


class TestUnsupportedLanguage:
    async def test_upload_rejects_unsupported_language(self, isolated_db):
        async with _new_client() as client:
            resp = await client.post(
                "/api/v1/resumes/upload",
                files={"file": ("resume.pdf", b"%PDF-1.4 fake", "application/pdf")},
                data={"language": "xx"},
            )
        assert resp.status_code == 400

    async def test_list_resumes_rejects_unsupported_language(self, isolated_db):
        async with _new_client() as client:
            resp = await client.get(
                "/api/v1/resumes/list", params={"language": "xx"}
            )
        assert resp.status_code == 400

    async def test_applications_board_rejects_unsupported_language(self, isolated_db):
        async with _new_client() as client:
            resp = await client.get("/api/v1/applications?language=xx")
        assert resp.status_code == 400


class TestTrackerLanguageIsolation:
    async def test_board_scoped_to_language_excludes_other_tenants(self, isolated_db):
        await isolated_db.create_application(
            job_id="job-en", resume_id="res-en", status="applied", language="en"
        )
        await isolated_db.create_application(
            job_id="job-fr", resume_id="res-fr", status="applied", language="fr"
        )

        async with _new_client() as client:
            en_board = (
                await client.get("/api/v1/applications?language=en")
            ).json()["columns"]
        assert len(en_board["applied"]) == 1
        assert en_board["applied"][0]["resume_id"] == "res-en"

        async with _new_client() as client:
            fr_board = (
                await client.get("/api/v1/applications?language=fr")
            ).json()["columns"]
        assert len(fr_board["applied"]) == 1
        assert fr_board["applied"][0]["resume_id"] == "res-fr"
