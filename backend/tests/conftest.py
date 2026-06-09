import uuid

import pytest
import sqlalchemy as sa
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import Settings
from app.core.database import Base, create_engine
from app.main import create_app
from app.models.mixins import BaseModelMixin
from app.models.tenant import Tenant


class StubEntity(BaseModelMixin, Base):
    """Entity de prueba para tests de repositorio y tenancy."""

    __tablename__ = "test_entity"

    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)


def is_postgres_available():
    try:
        import socket
        from urllib.parse import urlparse

        settings = Settings()
        parsed = urlparse(settings.database_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        sock = socket.create_connection((host, port), timeout=2)
        sock.close()
        return True
    except Exception:
        return False


def pytest_configure(config):
    config.addinivalue_line("markers", "needs_db: mark test as requiring a running PostgreSQL instance")


def pytest_collection_modifyitems(config, items):
    if is_postgres_available():
        return
    for item in items:
        if "needs_db" in item.keywords:
            item.add_marker(pytest.mark.skip(reason="PostgreSQL no disponible — saltando test que requiere DB real"))


@pytest.fixture
async def test_engine():
    settings = Settings()
    engine = create_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine):
    session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest.fixture
async def tenant_a(db_session):
    tenant = Tenant(nombre="Tenant A", slug="tenant-a")
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    return tenant


@pytest.fixture
async def tenant_b(db_session):
    tenant = Tenant(nombre="Tenant B", slug="tenant-b")
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    return tenant


@pytest.fixture
async def async_client():
    app = create_app()
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


@pytest.fixture
async def async_client_db_down():
    from unittest.mock import AsyncMock

    from app.core import dependencies

    app = create_app()

    async def override_get_db():
        mock_session = AsyncMock()
        mock_session.execute.side_effect = RuntimeError("Simulated DB failure")
        return mock_session

    app.dependency_overrides[dependencies.get_db] = override_get_db

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
