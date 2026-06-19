import uuid
from datetime import date

import pytest

from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.liquidacion import EstadoLiquidacion, Liquidacion
from app.models.salario_base import RolSalario
from app.models.user import User
from app.repositories.liquidacion_repository import LiquidacionRepository


@pytest.fixture
async def seed_liquidacion(db_session, tenant_a, tenant_b):
    user_a = User(
        email="liq_a@test.com", password_hash="hash",
        nombre="Docente", apellidos="A", tenant_id=tenant_a.id,
        legajo="L-LIQ-A",
    )
    user_b = User(
        email="liq_b@test.com", password_hash="hash",
        nombre="Docente", apellidos="B", tenant_id=tenant_b.id,
        legajo="L-LIQ-B",
    )
    db_session.add_all([user_a, user_b])
    await db_session.flush()

    carrera = Carrera(codigo="CAR_LIQ", nombre="Carrera Liq", activa=True, tenant_id=tenant_a.id)
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="COH_LIQ", anio=2026,
        vig_desde=date(2026, 1, 1), activa=True, tenant_id=tenant_a.id,
    )
    db_session.add(cohorte)
    await db_session.flush()

    liq1 = Liquidacion(
        tenant_id=tenant_a.id, cohorte_id=cohorte.id, periodo="2026-06",
        usuario_id=user_a.id, rol=RolSalario.PROFESOR,
        comisiones=[], monto_base=80000.00, monto_plus=0, total=80000.00,
        estado=EstadoLiquidacion.ABIERTA,
    )
    liq2 = Liquidacion(
        tenant_id=tenant_a.id, cohorte_id=cohorte.id, periodo="2026-06",
        usuario_id=user_b.id, rol=RolSalario.TUTOR,
        comisiones=[], monto_base=50000.00, monto_plus=0, total=50000.00,
        estado=EstadoLiquidacion.CERRADA,
    )
    db_session.add_all([liq1, liq2])
    await db_session.commit()

    return {
        "tenant_a_id": tenant_a.id,
        "tenant_b_id": tenant_b.id,
        "cohorte_id": cohorte.id,
        "user_a_id": user_a.id,
        "liq1_id": liq1.id,
        "liq2_id": liq2.id,
    }


@pytest.mark.needs_db
class TestLiquidacionRepository:
    async def test_list_by_cohorte_periodo(self, db_session, seed_liquidacion):
        d = seed_liquidacion
        repo = LiquidacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_cohorte_periodo(d["cohorte_id"], "2026-06")
        assert len(results) == 2

    async def test_list_by_cohorte_periodo_filters_estado(self, db_session, seed_liquidacion):
        d = seed_liquidacion
        repo = LiquidacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_cohorte_periodo(
            d["cohorte_id"], "2026-06", estado=EstadoLiquidacion.ABIERTA,
        )
        assert len(results) == 1
        assert results[0].estado == EstadoLiquidacion.ABIERTA

    async def test_get_by_usuario_cohorte_periodo(self, db_session, seed_liquidacion):
        d = seed_liquidacion
        repo = LiquidacionRepository(db_session, d["tenant_a_id"])
        result = await repo.get_by_usuario_cohorte_periodo(
            d["user_a_id"], d["cohorte_id"], "2026-06",
        )
        assert result is not None
        assert result.usuario_id == d["user_a_id"]

    async def test_get_by_usuario_returns_none_wrong_tenant(self, db_session, seed_liquidacion):
        d = seed_liquidacion
        repo = LiquidacionRepository(db_session, d["tenant_b_id"])
        result = await repo.get_by_usuario_cohorte_periodo(
            d["user_a_id"], d["cohorte_id"], "2026-06",
        )
        assert result is None

    async def test_cerrar_lote(self, db_session, seed_liquidacion):
        d = seed_liquidacion
        repo = LiquidacionRepository(db_session, d["tenant_a_id"])
        count = await repo.cerrar_lote(d["cohorte_id"], "2026-06")
        assert count == 1
        results = await repo.list_by_cohorte_periodo(
            d["cohorte_id"], "2026-06", estado=EstadoLiquidacion.ABIERTA,
        )
        assert len(results) == 0

    async def test_list_abiertas(self, db_session, seed_liquidacion):
        d = seed_liquidacion
        repo = LiquidacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_abiertas_by_cohorte_periodo(d["cohorte_id"], "2026-06")
        assert len(results) == 1
        assert results[0].estado == EstadoLiquidacion.ABIERTA

    async def test_soft_delete(self, db_session, seed_liquidacion):
        d = seed_liquidacion
        repo = LiquidacionRepository(db_session, d["tenant_a_id"])
        await repo.soft_delete(d["liq1_id"])
        result = await repo.get(d["liq1_id"])
        assert result is None
