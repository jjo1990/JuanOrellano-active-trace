from datetime import date

import pytest

from app.models.salario_base import RolSalario
from app.models.salario_plus import SalarioPlus
from app.repositories.salario_plus_repository import SalarioPlusRepository


@pytest.fixture
async def seed_salario_plus(db_session, tenant_a, tenant_b):
    sp_a1 = SalarioPlus(
        tenant_id=tenant_a.id, grupo="PROG", rol=RolSalario.PROFESOR,
        descripcion="Plus Programación", monto=15000.00,
        desde=date(2026, 1, 1), hasta=None,
    )
    sp_a2 = SalarioPlus(
        tenant_id=tenant_a.id, grupo="BD", rol=RolSalario.PROFESOR,
        descripcion="Plus Base de Datos", monto=10000.00,
        desde=date(2026, 1, 1), hasta=date(2026, 6, 30),
    )
    sp_b1 = SalarioPlus(
        tenant_id=tenant_b.id, grupo="PROG", rol=RolSalario.PROFESOR,
        descripcion="Plus Programación B", monto=20000.00,
        desde=date(2026, 1, 1), hasta=None,
    )
    db_session.add_all([sp_a1, sp_a2, sp_b1])
    await db_session.commit()
    return {
        "tenant_a_id": tenant_a.id,
        "tenant_b_id": tenant_b.id,
        "sp_a1_id": sp_a1.id,
        "sp_a2_id": sp_a2.id,
        "sp_b1_id": sp_b1.id,
    }


@pytest.mark.needs_db
class TestSalarioPlusRepository:
    async def test_list_by_grupo_filters(self, db_session, seed_salario_plus):
        d = seed_salario_plus
        repo = SalarioPlusRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_grupo("PROG")
        assert len(results) == 1
        assert results[0].grupo == "PROG"

    async def test_get_vigente_returns_active(self, db_session, seed_salario_plus):
        d = seed_salario_plus
        repo = SalarioPlusRepository(db_session, d["tenant_a_id"])
        result = await repo.get_vigente("PROG", "PROFESOR", date(2026, 6, 1))
        assert result is not None
        assert result.monto == 15000.00

    async def test_get_vigente_returns_none_past_hasta(self, db_session, seed_salario_plus):
        d = seed_salario_plus
        repo = SalarioPlusRepository(db_session, d["tenant_a_id"])
        result = await repo.get_vigente("BD", "PROFESOR", date(2026, 7, 1))
        assert result is None

    async def test_get_vigente_returns_none_wrong_grupo(self, db_session, seed_salario_plus):
        d = seed_salario_plus
        repo = SalarioPlusRepository(db_session, d["tenant_a_id"])
        result = await repo.get_vigente("MAT", "PROFESOR", date(2026, 3, 1))
        assert result is None

    async def test_existe_solapamiento_detects_overlap(self, db_session, seed_salario_plus):
        d = seed_salario_plus
        repo = SalarioPlusRepository(db_session, d["tenant_a_id"])
        assert await repo.existe_solapamiento("PROG", "PROFESOR", date(2026, 6, 1), None)

    async def test_multi_tenant_isolation(self, db_session, seed_salario_plus):
        d = seed_salario_plus
        repo_a = SalarioPlusRepository(db_session, d["tenant_a_id"])
        results_a = await repo_a.list()
        assert len(results_a) == 2
        repo_b = SalarioPlusRepository(db_session, d["tenant_b_id"])
        results_b = await repo_b.list()
        assert len(results_b) == 1

    async def test_create_assigns_tenant(self, db_session, seed_salario_plus):
        d = seed_salario_plus
        repo = SalarioPlusRepository(db_session, d["tenant_a_id"])
        entity = SalarioPlus(
            grupo="MAT", rol=RolSalario.PROFESOR,
            descripcion="Plus Matemática", monto=12000.00,
            desde=date(2026, 1, 1),
        )
        result = await repo.create(entity)
        assert result.tenant_id == d["tenant_a_id"]
        assert result.grupo == "MAT"

    async def test_soft_delete_works(self, db_session, seed_salario_plus):
        d = seed_salario_plus
        repo = SalarioPlusRepository(db_session, d["tenant_a_id"])
        await repo.soft_delete(d["sp_a1_id"])
        result = await repo.get(d["sp_a1_id"])
        assert result is None
