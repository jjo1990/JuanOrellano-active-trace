"""Tests de tenant isolation para Calificacion y UmbralMateria (C-10)."""

from datetime import date

import pytest

from app.models.asignacion import Asignacion
from app.models.calificacion import Calificacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.rol import Rol
from app.models.umbral_materia import UmbralMateria
from app.models.user import User
from app.models.version_padron import VersionPadron
from app.core.security import hash_password
from app.repositories.calificaciones_repository import CalificacionesRepository


@pytest.mark.needs_db
class TestCalificacionesTenant:
    async def test_calificacion_tenant_a_not_visible_from_tenant_b(self, db_session, tenant_a, tenant_b):
        entry_a, materia_a, _ = await _seed_tenant_data(db_session, tenant_a, "A")
        entry_b, materia_b, _ = await _seed_tenant_data(db_session, tenant_b, "B")

        repo_a = CalificacionesRepository(db_session, tenant_a.id)
        repo_b = CalificacionesRepository(db_session, tenant_b.id)

        cal = Calificacion(
            tenant_id=tenant_a.id,
            entrada_padron_id=entry_a.id,
            materia_id=materia_a.id,
            actividad="TP1",
            nota_numerica=70,
            origen="Importado",
        )
        await repo_a.create_calificacion(cal)
        await db_session.commit()

        cals_a = await repo_a.get_calificaciones_by_materia(materia_a.id)
        assert len(cals_a) == 1

        cals_b = await repo_b.get_calificaciones_by_materia(materia_a.id)
        assert len(cals_b) == 0

    async def test_umbral_tenant_a_not_visible_from_tenant_b(self, db_session, tenant_a, tenant_b):
        _, materia_a, user_a = await _seed_tenant_data(db_session, tenant_a, "A")
        _, materia_b, user_b = await _seed_tenant_data(db_session, tenant_b, "B")

        asign_a = await _seed_asignacion(db_session, tenant_a, materia_a, user_a)
        asign_b = await _seed_asignacion(db_session, tenant_b, materia_b, user_b)

        repo_a = CalificacionesRepository(db_session, tenant_a.id)
        repo_b = CalificacionesRepository(db_session, tenant_b.id)

        umbral = UmbralMateria(
            tenant_id=tenant_a.id,
            asignacion_id=asign_a.id,
            materia_id=materia_a.id,
            umbral_pct=80,
        )
        await repo_a._umbral_repo.create(umbral)
        await db_session.commit()

        result_a = await repo_a.get_umbral(materia_a.id, asign_a.id)
        assert result_a is not None
        assert result_a.umbral_pct == 80

        result_b = await repo_b.get_umbral(materia_a.id, asign_a.id)
        assert result_b is None

    async def test_tenant_b_counts_only_own_calificaciones(self, db_session, tenant_a, tenant_b):
        entry_a, materia_a, _ = await _seed_tenant_data(db_session, tenant_a, "A")
        entry_b, materia_b, _ = await _seed_tenant_data(db_session, tenant_b, "B")

        repo_a = CalificacionesRepository(db_session, tenant_a.id)
        repo_b = CalificacionesRepository(db_session, tenant_b.id)

        for i in range(3):
            cal = Calificacion(
                tenant_id=tenant_a.id,
                entrada_padron_id=entry_a.id,
                materia_id=materia_a.id,
                actividad=f"TP{i}",
                nota_numerica=70,
                origen="Importado",
            )
            await repo_a.create_calificacion(cal)

        for i in range(5):
            cal = Calificacion(
                tenant_id=tenant_b.id,
                entrada_padron_id=entry_b.id,
                materia_id=materia_b.id,
                actividad=f"TP{i}",
                nota_numerica=70,
                origen="Importado",
            )
            await repo_b.create_calificacion(cal)
        await db_session.commit()

        count_a = await repo_a.count_calificaciones(materia_a.id)
        count_b = await repo_b.count_calificaciones(materia_b.id)
        assert count_a == 3
        assert count_b == 5

    async def test_upsert_umbral_tenant_a_not_affect_tenant_b(self, db_session, tenant_a, tenant_b):
        _, materia_a, user_a = await _seed_tenant_data(db_session, tenant_a, "A")
        _, materia_b, user_b = await _seed_tenant_data(db_session, tenant_b, "B")

        asign_a = await _seed_asignacion(db_session, tenant_a, materia_a, user_a)
        asign_b = await _seed_asignacion(db_session, tenant_b, materia_b, user_b)

        repo_a = CalificacionesRepository(db_session, tenant_a.id)
        repo_b = CalificacionesRepository(db_session, tenant_b.id)

        umbral_a = UmbralMateria(
            tenant_id=tenant_a.id,
            asignacion_id=asign_a.id,
            materia_id=materia_a.id,
            umbral_pct=80,
        )
        await repo_a.upsert_umbral(umbral_a)
        await db_session.commit()

        result_b = await repo_b.get_umbral(materia_a.id, asign_a.id)
        assert result_b is None


async def _seed_tenant_data(db_session, tenant, suffix):
    carrera = Carrera(
        codigo=f"CARR-TN{suffix}", nombre=f"Carrera{suffix}", tenant_id=tenant.id,
    )
    db_session.add(carrera)
    await db_session.flush()
    materia = Materia(
        codigo=f"MAT-TN{suffix}", nombre=f"Materia{suffix}", tenant_id=tenant.id,
    )
    db_session.add(materia)
    await db_session.flush()
    cohorte = Cohorte(
        carrera_id=carrera.id, nombre=f"2026-T{suffix}", anio=2026,
        vig_desde=date(2026, 1, 1),
        tenant_id=tenant.id, activa=True,
    )
    db_session.add(cohorte)
    await db_session.flush()
    user = User(
        email=f"user_tn_{suffix.lower()}@test.com",
        password_hash=hash_password("pass123!"),
        nombre=f"User{suffix}", apellidos=f"Tenant{suffix}",
        tenant_id=tenant.id,
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
        version_id=version.id, nombre=f"Alumno{suffix}", apellidos=f"Apellido{suffix}",
    )
    db_session.add(entrada)
    await db_session.commit()
    await db_session.refresh(materia)
    await db_session.refresh(entrada)
    await db_session.refresh(user)
    return entrada, materia, user


async def _seed_asignacion(db_session, tenant, materia, user):
    rol = Rol(nombre=f"ROL_TN_{materia.codigo}", descripcion="Rol", tenant_id=tenant.id)
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
