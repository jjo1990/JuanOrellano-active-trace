import uuid
from datetime import date

import pytest

from app.models.salario_base import RolSalario, SalarioBase
from app.repositories.salario_base_repository import SalarioBaseRepository


@pytest.fixture
async def seed_salario_base(db_session, tenant_a, tenant_b):
    sb_a1 = SalarioBase(
        tenant_id=tenant_a.id, rol=RolSalario.PROFESOR, monto=80000.00,
        desde=date(2026, 1, 1), hasta=None,
    )
    sb_a2 = SalarioBase(
        tenant_id=tenant_a.id, rol=RolSalario.TUTOR, monto=50000.00,
        desde=date(2026, 1, 1), hasta=date(2026, 6, 30),
    )
    sb_b1 = SalarioBase(
        tenant_id=tenant_b.id, rol=RolSalario.PROFESOR, monto=90000.00,
        desde=date(2026, 1, 1), hasta=None,
    )
    db_session.add_all([sb_a1, sb_a2, sb_b1])
    await db_session.commit()
    return {
        "tenant_a_id": tenant_a.id,
        "tenant_b_id": tenant_b.id,
        "sb_a1_id": sb_a1.id,
        "sb_a2_id": sb_a2.id,
        "sb_b1_id": sb_b1.id,
    }


@pytest.mark.needs_db
class TestSalarioBaseRepository:
    async def test_get_returns_entity(self, db_session, seed_salario_base):
        d = seed_salario_base
        repo = SalarioBaseRepository(db_session, d["tenant_a_id"])
        result = await repo.get(d["sb_a1_id"])
        assert result is not None
        assert result.rol == RolSalario.PROFESOR
        assert result.monto == 80000.00

    async def test_get_returns_none_for_wrong_tenant(self, db_session, seed_salario_base):
        d = seed_salario_base
        repo = SalarioBaseRepository(db_session, d["tenant_b_id"])
        result = await repo.get(d["sb_a1_id"])
        assert result is None

    async def test_list_by_rol_filters(self, db_session, seed_salario_base):
        d = seed_salario_base
        repo = SalarioBaseRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_rol("PROFESOR")
        assert len(results) == 1
        assert results[0].rol == RolSalario.PROFESOR

    async def test_get_vigente_returns_active(self, db_session, seed_salario_base):
        d = seed_salario_base
        repo = SalarioBaseRepository(db_session, d["tenant_a_id"])
        result = await repo.get_vigente("PROFESOR", date(2026, 6, 1))
        assert result is not None
        assert result.monto == 80000.00

    async def test_get_vigente_returns_none_past_hasta(self, db_session, seed_salario_base):
        d = seed_salario_base
        repo = SalarioBaseRepository(db_session, d["tenant_a_id"])
        result = await repo.get_vigente("TUTOR", date(2026, 7, 1))
        assert result is None

    async def test_get_vigente_returns_none_before_desde(self, db_session, seed_salario_base):
        d = seed_salario_base
        repo = SalarioBaseRepository(db_session, d["tenant_a_id"])
        result = await repo.get_vigente("TUTOR", date(2025, 12, 1))
        assert result is None

    async def test_existe_solapamiento_detects_overlap(self, db_session, seed_salario_base):
        d = seed_salario_base
        repo = SalarioBaseRepository(db_session, d["tenant_a_id"])
        assert await repo.existe_solapamiento("PROFESOR", date(2026, 6, 1), None)

    async def test_existe_solapamiento_returns_false_no_overlap(self, db_session, seed_salario_base):
        d = seed_salario_base
        repo = SalarioBaseRepository(db_session, d["tenant_a_id"])
        assert not await repo.existe_solapamiento("COORDINADOR", date(2026, 1, 1), None)

    async def test_soft_delete_works(self, db_session, seed_salario_base):
        d = seed_salario_base
        repo = SalarioBaseRepository(db_session, d["tenant_a_id"])
        await repo.soft_delete(d["sb_a1_id"])
        result = await repo.get(d["sb_a1_id"])
        assert result is None

    async def test_create_assigns_tenant(self, db_session, seed_salario_base):
        d = seed_salario_base
        repo = SalarioBaseRepository(db_session, d["tenant_a_id"])
        entity = SalarioBase(
            rol=RolSalario.COORDINADOR, monto=100000.00,
            desde=date(2026, 1, 1),
        )
        result = await repo.create(entity)
        assert result.tenant_id == d["tenant_a_id"]
        assert result.rol == RolSalario.COORDINADOR

    async def test_multi_tenant_isolation(self, db_session, seed_salario_base):
        d = seed_salario_base
        repo_a = SalarioBaseRepository(db_session, d["tenant_a_id"])
        results_a = await repo_a.list()
        assert len(results_a) == 2
        repo_b = SalarioBaseRepository(db_session, d["tenant_b_id"])
        results_b = await repo_b.list()
        assert len(results_b) == 1
