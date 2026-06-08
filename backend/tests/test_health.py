"""RED → GREEN → TRIANGULATE: Health-check endpoint.

Task 5.x — Strict TDD.
"""
import pytest


@pytest.mark.asyncio
class TestHealthEndpoint:
    async def test_health_returns_200(self, async_client):
        response = await async_client.get("/health")
        assert response.status_code == 200

    async def test_health_has_status_ok(self, async_client):
        response = await async_client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    async def test_health_includes_database_field(self, async_client):
        response = await async_client.get("/health")
        data = response.json()
        assert "database" in data

    @pytest.mark.needs_db
    async def test_health_reports_db_up(self, async_client):
        response = await async_client.get("/health")
        data = response.json()
        assert data["database"] == "up"

    async def test_health_reports_db_down_on_failure(self, async_client_db_down):
        response = await async_client_db_down.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "down"
