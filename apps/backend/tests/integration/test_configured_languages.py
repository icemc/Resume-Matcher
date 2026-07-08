"""Integration tests for GET /api/v1/resumes/configured-languages."""

from httpx import ASGITransport, AsyncClient

from app.main import app


def _client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


class TestConfiguredLanguages:
    async def test_empty_database_returns_no_languages(self, isolated_db):
        async with _client() as client:
            resp = await client.get("/api/v1/resumes/configured-languages")
        assert resp.status_code == 200
        assert resp.json()["languages"] == []

    async def test_lists_distinct_languages_with_at_least_one_resume(self, isolated_db):
        await isolated_db.create_resume(content="# EN Resume", language="en")
        await isolated_db.create_resume(content="# FR Resume", language="fr")
        # A second English resume must not duplicate the "en" entry.
        await isolated_db.create_resume(content="# EN Resume 2", language="en")

        async with _client() as client:
            resp = await client.get("/api/v1/resumes/configured-languages")
        assert resp.status_code == 200
        assert resp.json()["languages"] == ["en", "fr"]
