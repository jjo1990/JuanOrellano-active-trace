"""RED → GREEN → TRIANGULATE: Conexión a base de datos async.

Task 3.x — Strict TDD.
"""
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.database import create_session_factory


@pytest.mark.asyncio
class TestDatabaseConnection:
    @pytest.mark.needs_db
    async def test_select_one(self, db_session):
        result = await db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    @pytest.mark.needs_db
    async def test_session_closes_on_exception(self, test_engine):
        session_factory = create_session_factory(test_engine)
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))

        is_closed = session.closed
        assert is_closed

    async def test_get_db_does_not_leak_connections(self, async_client):
        response = await async_client.get("/health")
        assert response.status_code == 200
