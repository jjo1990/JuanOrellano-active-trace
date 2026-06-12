"""Tests de tenant isolation para padrones (C-09)."""

import uuid
from datetime import date

import pytest

from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.user import User
from app.models.version_padron import VersionPadron
from app.repositories.padron_repository import PadronRepository
from app.core.security import hash_password


@pytest.fixture
async def tenant_fixtures(db_session, tenant_a, tenant_b):
    carrera_a = Carrera(codigo="CA-A", nombre="Carrera A", tenant_id=tenant_a.id)
    db_session.add(carrera_a)
    carrera_b = Carrera(codigo="CA-B", nombre="Carrera B", tenant_id=tenant_b.id)
    db_session.add(carrera_b)
    await db_session.flush()

    materia_a = Materia(codigo="M-A", nombre="Materia A", tenant_id=tenant_a.id)
    db_session.add(materia_a)
    materia_b = Materia(codigo="M-B", nombre="Materia B", tenant_id=tenant_b.id)
    db_session.add(materia_b)
    await db_session.flush()

    cohorte_a = Cohorte(
        carrera_id=carrera_a.id, nombre="C-A", anio=2026,
        vig_desde=date(2026, 1, 1), tenant_id=tenant_a.id, activa=True,
    )
    db_session.add(cohorte_a)
    cohorte_b = Cohorte(
        carrera_id=carrera_b.id, nombre="C-B", anio=2026,
        vig_desde=date(2026, 1, 1), tenant_id=tenant_b.id, activa=True,
    )
    db_session.add(cohorte_b)
    await db_session.flush()

    user_a = User(
        email="ua@test.com", password_hash=hash_password("pass"),
        nombre="UA", apellidos="A", tenant_id=tenant_a.id,
    )
    db_session.add(user_a)
    user_b = User(
        email="ub@test.com", password_hash=hash_password("pass"),
        nombre="UB", apellidos="B", tenant_id=tenant_b.id,
    )
    db_session.add(user_b)
    await db_session.commit()
    await db_session.refresh(materia_a)
    await db_session.refresh(materia_b)
    await db_session.refresh(cohorte_a)
    await db_session.refresh(cohorte_b)
    await db_session.refresh(user_a)
    await db_session.refresh(user_b)

    return {
        "materia_a": materia_a, "materia_b": materia_b,
        "cohorte_a": cohorte_a, "cohorte_b": cohorte_b,
        "user_a": user_a, "user_b": user_b,
        "tenant_a": tenant_a, "tenant_b": tenant_b,
    }


@pytest.mark.needs_db
class TestPadronTenantIsolation:

    async def test_version_tenant_a_no_visible_en_tenant_b(self, db_session, tenant_fixtures):
        fx = tenant_fixtures
        repo_a = PadronRepository(db_session, fx["tenant_a"].id)
        repo_b = PadronRepository(db_session, fx["tenant_b"].id)

        v = VersionPadron(
            materia_id=fx["materia_a"].id, cohorte_id=fx["cohorte_a"].id,
            cargado_por=fx["user_a"].id, activa=True,
        )
        await repo_a.create_version(v)
        await db_session.commit()

        versions_b = await repo_b.list_versions(materia_id=fx["materia_a"].id)
        assert len(versions_b) == 0

    async def test_entrada_tenant_a_no_incluida_en_tenant_b(self, db_session, tenant_fixtures):
        fx = tenant_fixtures
        repo_a = PadronRepository(db_session, fx["tenant_a"].id)
        repo_b = PadronRepository(db_session, fx["tenant_b"].id)

        v = VersionPadron(
            materia_id=fx["materia_a"].id, cohorte_id=fx["cohorte_a"].id,
            cargado_por=fx["user_a"].id, activa=True,
        )
        await repo_a.create_version(v)
        await db_session.flush()

        e = EntradaPadron(version_id=v.id, nombre="Test", apellidos="A")
        await repo_a.create_entrada(e)
        await db_session.commit()

        entradas_b = await repo_b.list_entradas(v.id)
        assert len(entradas_b) == 0

    async def test_vaciar_materia_a_no_afecta_tenant_b(self, db_session, tenant_fixtures):
        fx = tenant_fixtures
        repo_a = PadronRepository(db_session, fx["tenant_a"].id)
        repo_b = PadronRepository(db_session, fx["tenant_b"].id)

        v = VersionPadron(
            materia_id=fx["materia_b"].id, cohorte_id=fx["cohorte_b"].id,
            cargado_por=fx["user_b"].id, activa=True,
        )
        await repo_b.create_version(v)
        await db_session.flush()
        e = EntradaPadron(version_id=v.id, nombre="Test", apellidos="B")
        await repo_b.create_entrada(e)
        await db_session.commit()

        await repo_a.soft_delete_by_materia(fx["materia_b"].id)
        await db_session.commit()

        versions_b = await repo_b.list_versions(materia_id=fx["materia_b"].id)
        assert len(versions_b) == 1

    async def test_version_activa_tenant_a_no_afectada_por_tenant_b(self, db_session, tenant_fixtures):
        fx = tenant_fixtures
        repo_a = PadronRepository(db_session, fx["tenant_a"].id)
        repo_b = PadronRepository(db_session, fx["tenant_b"].id)

        v = VersionPadron(
            materia_id=fx["materia_a"].id, cohorte_id=fx["cohorte_a"].id,
            cargado_por=fx["user_a"].id, activa=True,
        )
        await repo_a.create_version(v)
        await db_session.flush()

        v_b = VersionPadron(
            materia_id=fx["materia_b"].id, cohorte_id=fx["cohorte_b"].id,
            cargado_por=fx["user_b"].id, activa=True,
        )
        await repo_b.create_version(v_b)
        await db_session.commit()

        active_a = await repo_a.get_active_version(fx["materia_a"].id, fx["cohorte_a"].id)
        assert active_a is not None
        assert active_a.activa is True

    async def test_soft_delete_mas_create_en_otro_tenant(self, db_session, tenant_fixtures):
        fx = tenant_fixtures
        repo_a = PadronRepository(db_session, fx["tenant_a"].id)
        repo_b = PadronRepository(db_session, fx["tenant_b"].id)

        v = VersionPadron(
            materia_id=fx["materia_a"].id, cohorte_id=fx["cohorte_a"].id,
            cargado_por=fx["user_a"].id, activa=True,
        )
        await repo_a.create_version(v)
        await db_session.flush()
        vid = v.id

        await repo_a.soft_delete_by_materia(fx["materia_a"].id)
        await db_session.commit()

        v_restored = await repo_a.get_version(vid)
        assert v_restored is None

        v_b = VersionPadron(
            materia_id=fx["materia_b"].id, cohorte_id=fx["cohorte_b"].id,
            cargado_por=fx["user_b"].id, activa=True,
        )
        await repo_b.create_version(v_b)
        await db_session.commit()

        all_b = await repo_b.list_versions(materia_id=fx["materia_b"].id)
        assert len(all_b) == 1
        assert all_b[0].activa is True
