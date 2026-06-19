import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.models.asignacion import Asignacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.rol import Rol
from app.models.user import User
from app.repositories.user_repository import UserRepository


@pytest.fixture
async def seed_user_search(db_session, tenant_a):
    users = [
        User(email="gonzalez@test.com", password_hash="hash",
             nombre="Maria", apellidos="Gonzalez", legajo="L-001", tenant_id=tenant_a.id),
        User(email="gonzalo@test.com", password_hash="hash",
             nombre="Gonzalo", apellidos="Perez", legajo="L-002", tenant_id=tenant_a.id),
        User(email="martinez@test.com", password_hash="hash",
             nombre="Juan", apellidos="Martinez", legajo="L-003", tenant_id=tenant_a.id),
        User(email="luis@test.com", password_hash="hash",
             nombre="Luis", apellidos="Gomez", legajo="LEG-9999", tenant_id=tenant_a.id),
    ]
    db_session.add_all(users)
    await db_session.flush()

    soft_deleted = User(
        email="deleted@test.com", password_hash="hash",
        nombre="Deleted", apellidos="User", legajo="L-DEL",
        tenant_id=tenant_a.id, deleted_at=datetime.now(timezone.utc),
    )
    db_session.add(soft_deleted)
    await db_session.commit()

    return {
        "user_ids": {u.email: u.id for u in users},
        "tenant_a_id": tenant_a.id,
    }


@pytest.mark.needs_db
class TestSearchByName:
    async def test_search_by_name_partial(self, db_session, seed_user_search):
        d = seed_user_search
        repo = UserRepository(db_session, d["tenant_a_id"])
        results = await repo.search_by_name("gon")
        assert len(results) >= 1
        emails = [r.email for r in results]
        assert "gonzalez@test.com" in emails or "gonzalo@test.com" in emails

    async def test_search_by_apellido(self, db_session, seed_user_search):
        d = seed_user_search
        repo = UserRepository(db_session, d["tenant_a_id"])
        results = await repo.search_by_name("martinez")
        assert len(results) == 1
        assert results[0].email == "martinez@test.com"

    async def test_search_case_insensitive(self, db_session, seed_user_search):
        d = seed_user_search
        repo = UserRepository(db_session, d["tenant_a_id"])
        results_lower = await repo.search_by_name("gonzalez")
        results_upper = await repo.search_by_name("GONZALEZ")
        assert len(results_lower) == len(results_upper)

    async def test_limite_respected(self, db_session, seed_user_search):
        d = seed_user_search
        repo = UserRepository(db_session, d["tenant_a_id"])
        results = await repo.search_by_name("a", limite=2)
        assert len(results) <= 2

    async def test_search_by_legajo(self, db_session, seed_user_search):
        d = seed_user_search
        repo = UserRepository(db_session, d["tenant_a_id"])
        results = await repo.search_by_name("LEG-9999")
        assert len(results) == 1
        assert results[0].legajo == "LEG-9999"

    async def test_search_by_legajo_partial(self, db_session, seed_user_search):
        d = seed_user_search
        repo = UserRepository(db_session, d["tenant_a_id"])
        results = await repo.search_by_name("L-00")
        assert len(results) >= 2

    async def test_tenant_scope(self, db_session, seed_user_search, tenant_b):
        d = seed_user_search
        repo_b = UserRepository(db_session, tenant_b.id)
        results = await repo_b.search_by_name("gon")
        assert len(results) == 0

    async def test_excludes_soft_deleted(self, db_session, seed_user_search):
        d = seed_user_search
        repo = UserRepository(db_session, d["tenant_a_id"])
        results = await repo.search_by_name("deleted")
        assert len(results) == 0

    async def test_empty_query_returns_empty(self, db_session, seed_user_search):
        d = seed_user_search
        repo = UserRepository(db_session, d["tenant_a_id"])
        results = await repo.search_by_name("")
        assert len(results) == 0

    async def test_no_match_returns_empty(self, db_session, seed_user_search):
        d = seed_user_search
        repo = UserRepository(db_session, d["tenant_a_id"])
        results = await repo.search_by_name("xyz123_nonexistent")
        assert len(results) == 0

    async def test_search_with_roles_filter(self, db_session, seed_user_search, tenant_a):
        d = seed_user_search
        repo = UserRepository(db_session, d["tenant_a_id"])

        rol = Rol(nombre="PROFESOR_SEARCH", descripcion="Prof Search", tenant_id=tenant_a.id)
        db_session.add(rol)
        await db_session.flush()

        materia = Materia(codigo="MAT_SRCH", nombre="Mat Search", activa=True, tenant_id=tenant_a.id)
        db_session.add(materia)
        await db_session.flush()

        carrera = Carrera(codigo="CAR_SRCH", nombre="Car Search", activa=True, tenant_id=tenant_a.id)
        db_session.add(carrera)
        await db_session.flush()

        cohorte = Cohorte(
            carrera_id=carrera.id, nombre="COH_SRCH", anio=2026,
            vig_desde=date(2026, 1, 1), activa=True, tenant_id=tenant_a.id,
        )
        db_session.add(cohorte)
        await db_session.flush()

        gonzalez_id = d["user_ids"]["gonzalez@test.com"]
        asig = Asignacion(
            usuario_id=gonzalez_id, rol_id=rol.id,
            materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
            comisiones=[], desde=date(2026, 1, 1), hasta=None,
            tenant_id=tenant_a.id,
        )
        db_session.add(asig)
        await db_session.commit()

        results = await repo.search_by_name("gon", roles=["PROFESOR_SEARCH"])
        assert len(results) >= 1

    async def test_search_with_nonexistent_roles_returns_empty(self, db_session, seed_user_search):
        d = seed_user_search
        repo = UserRepository(db_session, d["tenant_a_id"])
        results = await repo.search_by_name("gon", roles=["ROL_INEXISTENTE"])
        assert len(results) == 0
