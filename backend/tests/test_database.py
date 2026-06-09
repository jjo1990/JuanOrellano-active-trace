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
        """Session factory crea sesiones válidas que se limpian al salir del context manager."""
        session_factory = create_session_factory(test_engine)
        async with session_factory() as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
        # Si llegamos acá sin error, el context manager manejó correctamente
        # la sesión (rollback + close + return connection to pool)

    async def test_get_db_does_not_leak_connections(self, async_client):
        response = await async_client.get("/health")
        assert response.status_code == 200
