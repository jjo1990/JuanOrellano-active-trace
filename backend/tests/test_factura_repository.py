import uuid
from datetime import datetime, timezone

import pytest

from app.models.factura import EstadoFactura, Factura
from app.models.user import User
from app.repositories.factura_repository import FacturaRepository


@pytest.fixture
async def seed_factura(db_session, tenant_a, tenant_b):
    user_a = User(
        email="fact_a@test.com", password_hash="hash",
        nombre="Docente", apellidos="Fact A", tenant_id=tenant_a.id,
        legajo="L-FACT-A",
    )
    user_b = User(
        email="fact_b@test.com", password_hash="hash",
        nombre="Docente", apellidos="Fact B", tenant_id=tenant_a.id,
        legajo="L-FACT-B",
    )
    db_session.add_all([user_a, user_b])
    await db_session.flush()

    f1 = Factura(
        tenant_id=tenant_a.id, usuario_id=user_a.id, periodo="2026-06",
        detalle="Honorarios junio", estado=EstadoFactura.PENDIENTE,
        cargada_at=datetime.now(timezone.utc),
    )
    f2 = Factura(
        tenant_id=tenant_a.id, usuario_id=user_b.id, periodo="2026-06",
        detalle="Honorarios junio B", estado=EstadoFactura.ABONADA,
        cargada_at=datetime.now(timezone.utc),
        abonada_at=datetime.now(timezone.utc),
    )
    f3 = Factura(
        tenant_id=tenant_b.id, usuario_id=user_a.id, periodo="2026-05",
        detalle="Honorarios mayo", estado=EstadoFactura.PENDIENTE,
        cargada_at=datetime.now(timezone.utc),
    )
    db_session.add_all([f1, f2, f3])
    await db_session.commit()

    return {
        "tenant_a_id": tenant_a.id,
        "tenant_b_id": tenant_b.id,
        "user_a_id": user_a.id,
        "user_b_id": user_b.id,
        "f1_id": f1.id,
        "f2_id": f2.id,
        "f3_id": f3.id,
    }


@pytest.mark.needs_db
class TestFacturaRepository:
    async def test_list_with_filters_by_estado(self, db_session, seed_factura):
        d = seed_factura
        repo = FacturaRepository(db_session, d["tenant_a_id"])
        results = await repo.list_with_filters(estado="PENDIENTE")
        assert len(results) == 1
        assert results[0].estado == EstadoFactura.PENDIENTE

    async def test_list_with_filters_by_usuario(self, db_session, seed_factura):
        d = seed_factura
        repo = FacturaRepository(db_session, d["tenant_a_id"])
        results = await repo.list_with_filters(usuario_id=d["user_a_id"])
        assert len(results) == 1

    async def test_list_with_filters_by_periodo(self, db_session, seed_factura):
        d = seed_factura
        repo = FacturaRepository(db_session, d["tenant_a_id"])
        results = await repo.list_with_filters(periodo="2026-06")
        assert len(results) == 2

    async def test_list_all(self, db_session, seed_factura):
        d = seed_factura
        repo = FacturaRepository(db_session, d["tenant_a_id"])
        results = await repo.list_with_filters()
        assert len(results) == 2

    async def test_multi_tenant_isolation(self, db_session, seed_factura):
        d = seed_factura
        repo_a = FacturaRepository(db_session, d["tenant_a_id"])
        results_a = await repo_a.list_with_filters()
        assert len(results_a) == 2
        repo_b = FacturaRepository(db_session, d["tenant_b_id"])
        results_b = await repo_b.list_with_filters()
        assert len(results_b) == 1

    async def test_create(self, db_session, seed_factura):
        d = seed_factura
        repo = FacturaRepository(db_session, d["tenant_a_id"])
        entity = Factura(
            usuario_id=d["user_a_id"], periodo="2026-07",
            detalle="Honorarios julio", estado=EstadoFactura.PENDIENTE,
            cargada_at=datetime.now(timezone.utc),
        )
        result = await repo.create(entity)
        assert result.tenant_id == d["tenant_a_id"]
        assert result.periodo == "2026-07"
