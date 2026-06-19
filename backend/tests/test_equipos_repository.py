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
from app.repositories.asignacion_repository import AsignacionRepository


@pytest.fixture
async def seed_equipo_repo(db_session, tenant_a):
    """Seed data for repository tests."""
    user1 = User(
        email="repo1@test.com", password_hash="hash",
        nombre="Juan", apellidos="Perez", tenant_id=tenant_a.id,
        legajo="L-001",
    )
    user2 = User(
        email="repo2@test.com", password_hash="hash",
        nombre="Maria", apellidos="Gomez", tenant_id=tenant_a.id,
        legajo="L-002",
    )
    db_session.add_all([user1, user2])
    await db_session.flush()

    rol = Rol(nombre="PROFESOR_REPO", descripcion="Prof Repo", tenant_id=tenant_a.id)
    db_session.add(rol)
    await db_session.flush()

    materia = Materia(codigo="MAT_REPO", nombre="Materia Repo", activa=True, tenant_id=tenant_a.id)
    db_session.add(materia)
    await db_session.flush()

    carrera = Carrera(codigo="CAR_REPO", nombre="Carrera Repo", activa=True, tenant_id=tenant_a.id)
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="COH_REPO", anio=2026,
        vig_desde=date(2026, 1, 1), activa=True, tenant_id=tenant_a.id,
    )
    db_session.add(cohorte)
    await db_session.flush()

    asig1 = Asignacion(
        usuario_id=user1.id, rol_id=rol.id,
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        comisiones=["A"], desde=date(2026, 1, 1), hasta=date(2026, 12, 31),
        tenant_id=tenant_a.id,
    )
    asig2 = Asignacion(
        usuario_id=user2.id, rol_id=rol.id,
        materia_id=materia.id, carrera_id=carrera.id, cohorte_id=cohorte.id,
        comisiones=["B"], desde=date(2026, 1, 1), hasta=None,
        tenant_id=tenant_a.id,
    )
    db_session.add_all([asig1, asig2])
    await db_session.commit()

    return {
        "user1_id": user1.id,
        "user2_id": user2.id,
        "rol_id": rol.id,
        "materia_id": materia.id,
        "carrera_id": carrera.id,
        "cohorte_id": cohorte.id,
        "asig1_id": asig1.id,
        "asig2_id": asig2.id,
        "tenant_a_id": tenant_a.id,
    }


@pytest.mark.needs_db
class TestListWithJoins:
    async def test_returns_assignments_with_eager_loaded_relations(self, db_session, seed_equipo_repo):
        d = seed_equipo_repo
        repo = AsignacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_with_joins()

        assert len(results) >= 2
        for a in results:
            assert a.usuario is not None
            assert a.rol is not None
            assert a.materia is not None
            assert a.carrera is not None
            assert a.cohorte is not None

    async def test_list_with_joins_filters_by_usuario_id(self, db_session, seed_equipo_repo):
        d = seed_equipo_repo
        repo = AsignacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_with_joins(usuario_id=d["user1_id"])
        assert len(results) == 1
        assert results[0].usuario_id == d["user1_id"]

    async def test_list_with_joins_filters_by_materia_id(self, db_session, seed_equipo_repo):
        d = seed_equipo_repo
        repo = AsignacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_with_joins(materia_id=d["materia_id"])
        assert len(results) == 2

    async def test_list_with_joins_filters_by_rol_id(self, db_session, seed_equipo_repo):
        d = seed_equipo_repo
        repo = AsignacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_with_joins(rol_id=d["rol_id"])
        assert len(results) == 2

    async def test_list_with_joins_filters_vigentes(self, db_session, seed_equipo_repo):
        d = seed_equipo_repo
        repo = AsignacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_with_joins(vigente=True)
        assert all(a.desde <= date.today() for a in results)

    async def test_list_with_joins_excludes_soft_deleted(self, db_session, seed_equipo_repo):
        d = seed_equipo_repo
        repo = AsignacionRepository(db_session, d["tenant_a_id"])

        await repo.soft_delete(d["asig1_id"])
        await db_session.commit()

        results = await repo.list_with_joins()
        ids = [a.id for a in results]
        assert d["asig1_id"] not in ids
        assert d["asig2_id"] in ids

    async def test_list_with_joins_tenant_scope(self, db_session, seed_equipo_repo, tenant_b):
        d = seed_equipo_repo
        repo_b = AsignacionRepository(db_session, tenant_b.id)
        results = await repo_b.list_with_joins()
        assert len(results) == 0


@pytest.mark.needs_db
class TestBulkCreate:
    async def test_bulk_create_inserts_multiple(self, db_session, seed_equipo_repo):
        d = seed_equipo_repo
        repo = AsignacionRepository(db_session, d["tenant_a_id"])

        new_user = User(
            email="bulk1@test.com", password_hash="hash",
            nombre="Bulk", apellidos="Test", tenant_id=d["tenant_a_id"],
        )
        db_session.add(new_user)
        await db_session.flush()

        entities = [
            Asignacion(
                usuario_id=new_user.id, rol_id=d["rol_id"],
                materia_id=d["materia_id"], carrera_id=d["carrera_id"],
                cohorte_id=d["cohorte_id"], comisiones=["A"],
                desde=date(2026, 1, 1), hasta=date(2026, 6, 30),
            ),
            Asignacion(
                usuario_id=new_user.id, rol_id=d["rol_id"],
                materia_id=d["materia_id"], carrera_id=d["carrera_id"],
                cohorte_id=d["cohorte_id"], comisiones=["B"],
                desde=date(2026, 7, 1), hasta=None,
            ),
        ]
        results = await repo.bulk_create(entities)
        await db_session.commit()

        assert len(results) == 2
        assert all(r.tenant_id == d["tenant_a_id"] for r in results)
        assert all(r.id is not None for r in results)

    async def test_bulk_create_empty_list(self, db_session, seed_equipo_repo):
        d = seed_equipo_repo
        repo = AsignacionRepository(db_session, d["tenant_a_id"])
        results = await repo.bulk_create([])
        assert len(results) == 0


@pytest.mark.needs_db
class TestBulkUpdateVigencia:
    async def test_bulk_update_vigencia_updates_matching(self, db_session, seed_equipo_repo):
        d = seed_equipo_repo
        repo = AsignacionRepository(db_session, d["tenant_a_id"])

        nueva_desde = date(2027, 1, 1)
        nueva_hasta = date(2027, 12, 31)
        count = await repo.bulk_update_vigencia(
            materia_id=d["materia_id"],
            carrera_id=d["carrera_id"],
            cohorte_id=d["cohorte_id"],
            desde=nueva_desde,
            hasta=nueva_hasta,
        )
        await db_session.commit()

        assert count >= 2

        stmt = select(Asignacion).where(Asignacion.materia_id == d["materia_id"])
        result = await db_session.execute(stmt)
        for a in result.scalars():
            assert a.desde == nueva_desde
            assert a.hasta == nueva_hasta

    async def test_bulk_update_vigencia_no_match_returns_zero(self, db_session, seed_equipo_repo):
        d = seed_equipo_repo
        repo = AsignacionRepository(db_session, d["tenant_a_id"])

        fake_id = uuid.uuid4()
        count = await repo.bulk_update_vigencia(
            materia_id=fake_id,
            carrera_id=d["carrera_id"],
            cohorte_id=d["cohorte_id"],
            desde=date(2027, 1, 1),
            hasta=None,
        )
        assert count == 0

    async def test_bulk_update_vigencia_respects_tenant(self, db_session, seed_equipo_repo, tenant_b):
        d = seed_equipo_repo
        repo_b = AsignacionRepository(db_session, tenant_b.id)

        count = await repo_b.bulk_update_vigencia(
            materia_id=d["materia_id"],
            carrera_id=d["carrera_id"],
            cohorte_id=d["cohorte_id"],
            desde=date(2027, 1, 1),
            hasta=None,
        )
        assert count == 0

    async def test_bulk_update_vigencia_only_desde(self, db_session, seed_equipo_repo):
        d = seed_equipo_repo
        repo = AsignacionRepository(db_session, d["tenant_a_id"])

        nueva_desde = date(2027, 1, 1)
        count = await repo.bulk_update_vigencia(
            materia_id=d["materia_id"],
            carrera_id=d["carrera_id"],
            cohorte_id=d["cohorte_id"],
            desde=nueva_desde,
            hasta=None,
        )
        await db_session.commit()

        assert count >= 2
        stmt = select(Asignacion).where(Asignacion.materia_id == d["materia_id"])
        result = await db_session.execute(stmt)
        for a in result.scalars():
            assert a.desde == nueva_desde

    async def test_bulk_update_vigencia_only_hasta(self, db_session, seed_equipo_repo):
        d = seed_equipo_repo
        repo = AsignacionRepository(db_session, d["tenant_a_id"])

        nueva_hasta = date(2027, 12, 31)
        count = await repo.bulk_update_vigencia(
            materia_id=d["materia_id"],
            carrera_id=d["carrera_id"],
            cohorte_id=d["cohorte_id"],
            desde=None,
            hasta=nueva_hasta,
        )
        await db_session.commit()

        assert count >= 2
        stmt = select(Asignacion).where(Asignacion.materia_id == d["materia_id"])
        result = await db_session.execute(stmt)
        for a in result.scalars():
            assert a.hasta == nueva_hasta


@pytest.mark.needs_db
class TestListByEquipo:
    async def test_list_by_equipo_full_filter(self, db_session, seed_equipo_repo):
        d = seed_equipo_repo
        repo = AsignacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_equipo(
            materia_id=d["materia_id"],
            carrera_id=d["carrera_id"],
            cohorte_id=d["cohorte_id"],
        )
        assert len(results) >= 2

    async def test_list_by_equipo_partial_filter_materia_only(self, db_session, seed_equipo_repo):
        d = seed_equipo_repo
        repo = AsignacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_equipo(
            materia_id=d["materia_id"],
        )
        assert len(results) >= 2

    async def test_list_by_equipo_no_match(self, db_session, seed_equipo_repo):
        d = seed_equipo_repo
        repo = AsignacionRepository(db_session, d["tenant_a_id"])
        results = await repo.list_by_equipo(
            materia_id=uuid.uuid4(),
            carrera_id=d["carrera_id"],
            cohorte_id=d["cohorte_id"],
        )
        assert len(results) == 0

    async def test_list_by_equipo_excludes_soft_deleted(self, db_session, seed_equipo_repo):
        d = seed_equipo_repo
        repo = AsignacionRepository(db_session, d["tenant_a_id"])

        await repo.soft_delete(d["asig1_id"])
        await db_session.commit()

        results = await repo.list_by_equipo(
            materia_id=d["materia_id"],
            carrera_id=d["carrera_id"],
            cohorte_id=d["cohorte_id"],
        )
        ids = [a.id for a in results]
        assert d["asig1_id"] not in ids
        assert d["asig2_id"] in ids
