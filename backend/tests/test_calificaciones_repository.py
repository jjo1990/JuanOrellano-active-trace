"""Tests triangulación para CalificacionesRepository (C-10)."""

from datetime import date

import pytest

from app.models.calificacion import Calificacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.umbral_materia import UmbralMateria
from app.models.user import User
from app.models.version_padron import VersionPadron
from app.models.asignacion import Asignacion
from app.models.rol import Rol
from app.core.security import hash_password
from app.repositories.calificaciones_repository import CalificacionesRepository


@pytest.mark.needs_db
class TestCalificacionesRepository:
    async def test_batch_create_500_calificaciones(self, db_session, tenant_a):
        entry, materia, _ = await _seed_data(db_session, tenant_a)
        repo = CalificacionesRepository(db_session, tenant_a.id)
        calificaciones = []
        for i in range(500):
            cal = Calificacion(
                tenant_id=tenant_a.id,
                entrada_padron_id=entry.id,
                materia_id=materia.id,
                actividad=f"TP{i}",
                nota_numerica=float(i % 101),
                origen="Importado",
            )
            calificaciones.append(cal)
        result = await repo.create_calificaciones_batch(calificaciones)
        assert len(result) == 500

        count = await repo.count_calificaciones(materia.id)
        assert count == 500

    async def test_get_calificaciones_by_materia_excludes_deleted(self, db_session, tenant_a):
        entry, materia, _ = await _seed_data(db_session, tenant_a)
        repo = CalificacionesRepository(db_session, tenant_a.id)
        cal = Calificacion(
            tenant_id=tenant_a.id,
            entrada_padron_id=entry.id,
            materia_id=materia.id,
            actividad="TP1",
            nota_numerica=70,
            origen="Manual",
        )
        await repo.create_calificacion(cal)
        await db_session.commit()

        cal2 = Calificacion(
            tenant_id=tenant_a.id,
            entrada_padron_id=entry.id,
            materia_id=materia.id,
            actividad="TP2",
            nota_numerica=80,
            origen="Manual",
        )
        await repo.create_calificacion(cal2)
        await db_session.commit()

        deleted = await repo.soft_delete_by_materia(materia.id)
        assert deleted == 2

        cal_list = await repo.get_calificaciones_by_materia(materia.id)
        assert len(cal_list) == 0

    async def test_soft_delete_umbral(self, db_session, tenant_a):
        _, materia, user = await _seed_data(db_session, tenant_a)
        asign = await _seed_asignacion(db_session, tenant_a, materia, user)
        repo = CalificacionesRepository(db_session, tenant_a.id)
        umbral = UmbralMateria(
            tenant_id=tenant_a.id,
            asignacion_id=asign.id,
            materia_id=materia.id,
            umbral_pct=70,
        )
        created = await repo._umbral_repo.create(umbral)
        await db_session.commit()

        await repo._umbral_repo.soft_delete(created.id)

        result = await repo.get_umbral(materia.id, asign.id)
        assert result is None

    async def test_upsert_umbral_creates_if_not_exists(self, db_session, tenant_a):
        _, materia, user = await _seed_data(db_session, tenant_a)
        asign = await _seed_asignacion(db_session, tenant_a, materia, user)
        repo = CalificacionesRepository(db_session, tenant_a.id)
        umbral = UmbralMateria(
            tenant_id=tenant_a.id,
            asignacion_id=asign.id,
            materia_id=materia.id,
            umbral_pct=80,
            valores_aprobatorios=["Aprobado"],
        )
        result = await repo.upsert_umbral(umbral)
        assert result.umbral_pct == 80
        assert result.valores_aprobatorios == ["Aprobado"]

    async def test_upsert_umbral_updates_if_exists(self, db_session, tenant_a):
        _, materia, user = await _seed_data(db_session, tenant_a)
        asign = await _seed_asignacion(db_session, tenant_a, materia, user)
        repo = CalificacionesRepository(db_session, tenant_a.id)
        umbral1 = UmbralMateria(
            tenant_id=tenant_a.id,
            asignacion_id=asign.id,
            materia_id=materia.id,
            umbral_pct=70,
        )
        await repo.upsert_umbral(umbral1)
        await db_session.commit()

        umbral2 = UmbralMateria(
            tenant_id=tenant_a.id,
            asignacion_id=asign.id,
            materia_id=materia.id,
            umbral_pct=90,
            valores_aprobatorios=["Excelente"],
        )
        result = await repo.upsert_umbral(umbral2)
        assert result.umbral_pct == 90
        assert result.valores_aprobatorios == ["Excelente"]

    async def test_get_calificaciones_by_entrada(self, db_session, tenant_a):
        entry, materia, _ = await _seed_data(db_session, tenant_a)
        repo = CalificacionesRepository(db_session, tenant_a.id)
        cal1 = Calificacion(
            tenant_id=tenant_a.id,
            entrada_padron_id=entry.id,
            materia_id=materia.id,
            actividad="TP1",
            nota_numerica=60,
            origen="Importado",
        )
        cal2 = Calificacion(
            tenant_id=tenant_a.id,
            entrada_padron_id=entry.id,
            materia_id=materia.id,
            actividad="TP2",
            nota_numerica=80,
            origen="Importado",
        )
        await repo.create_calificacion(cal1)
        await repo.create_calificacion(cal2)
        await db_session.commit()

        result = await repo.get_calificaciones_by_entrada(entry.id)
        assert len(result) == 2


async def _seed_data(db_session, tenant):
    carrera = Carrera(codigo="CARR-REPO", nombre="CarreraRepo", tenant_id=tenant.id)
    db_session.add(carrera)
    await db_session.flush()
    materia = Materia(codigo="MAT-REPO", nombre="MateriaRepo", tenant_id=tenant.id)
    db_session.add(materia)
    await db_session.flush()
    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="2026-R", anio=2026,
        vig_desde=date(2026, 1, 1),
        tenant_id=tenant.id, activa=True,
    )
    db_session.add(cohorte)
    await db_session.flush()
    user = User(
        email="repouser@test.com", password_hash=hash_password("pass123!"),
        nombre="Repo", apellidos="User", tenant_id=tenant.id,
    )
    db_session.add(user)
    await db_session.flush()
    version = VersionPadron(
        tenant_id=tenant.id,
        materia_id=materia.id, cohorte_id=cohorte.id,
        cargado_por=user.id, activa=True,
    )
    db_session.add(version)
    await db_session.flush()
    entrada = EntradaPadron(
        tenant_id=tenant.id,
        version_id=version.id, nombre="Maria", apellidos="Gomez",
    )
    db_session.add(entrada)
    await db_session.commit()
    await db_session.refresh(materia)
    await db_session.refresh(entrada)
    await db_session.refresh(user)
    return entrada, materia, user


async def _seed_asignacion(db_session, tenant, materia, user):
    rol = Rol(nombre="REPO_ROL", descripcion="Repo Rol", tenant_id=tenant.id)
    db_session.add(rol)
    await db_session.flush()
    asign = Asignacion(
        tenant_id=tenant.id,
        usuario_id=user.id,
        rol_id=rol.id,
        materia_id=materia.id,
        desde=date(2026, 1, 1),
    )
    db_session.add(asign)
    await db_session.commit()
    await db_session.refresh(asign)
    return asign
