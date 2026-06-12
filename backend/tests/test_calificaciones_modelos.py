"""Tests para modelos Calificacion y UmbralMateria (C-10)."""

from datetime import date

import pytest
import sqlalchemy as sa
from sqlalchemy import select

from app.models.calificacion import Calificacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.rol import Rol
from app.models.umbral_materia import UmbralMateria
from app.models.user import User
from app.models.version_padron import VersionPadron
from app.models.asignacion import Asignacion
from app.core.security import hash_password


@pytest.mark.needs_db
class TestCalificacionModel:
    async def test_create_with_nota_numerica(self, db_session, tenant_a):
        entry, materia, _ = await _seed_data(db_session, tenant_a)
        cal = Calificacion(
            tenant_id=tenant_a.id,
            entrada_padron_id=entry.id,
            materia_id=materia.id,
            actividad="Examen (Real)",
            nota_numerica=85.00,
            nota_textual=None,
            origen="Importado",
        )
        db_session.add(cal)
        await db_session.commit()
        await db_session.refresh(cal)
        assert cal.nota_numerica == 85.00
        assert cal.nota_textual is None
        assert cal.origen == "Importado"

    async def test_create_with_nota_textual(self, db_session, tenant_a):
        entry, materia, _ = await _seed_data(db_session, tenant_a)
        cal = Calificacion(
            tenant_id=tenant_a.id,
            entrada_padron_id=entry.id,
            materia_id=materia.id,
            actividad="Satisfactorio",
            nota_numerica=None,
            nota_textual="Satisfactorio",
            origen="Manual",
        )
        db_session.add(cal)
        await db_session.commit()
        await db_session.refresh(cal)
        assert cal.nota_textual == "Satisfactorio"
        assert cal.nota_numerica is None

    async def test_origen_importado_valido(self, db_session, tenant_a):
        entry, materia, _ = await _seed_data(db_session, tenant_a)
        cal = Calificacion(
            tenant_id=tenant_a.id,
            entrada_padron_id=entry.id,
            materia_id=materia.id,
            actividad="TP",
            nota_numerica=70.00,
            origen="Importado",
        )
        db_session.add(cal)
        await db_session.commit()
        assert cal.origen == "Importado"

    async def test_origen_manual_valido(self, db_session, tenant_a):
        entry, materia, _ = await _seed_data(db_session, tenant_a)
        cal = Calificacion(
            tenant_id=tenant_a.id,
            entrada_padron_id=entry.id,
            materia_id=materia.id,
            actividad="TP",
            nota_numerica=50.00,
            origen="Manual",
        )
        db_session.add(cal)
        await db_session.commit()
        assert cal.origen == "Manual"

    async def test_origen_invalido_viola_check_constraint(self, db_session, tenant_a):
        entry, materia, _ = await _seed_data(db_session, tenant_a)
        cal = Calificacion(
            tenant_id=tenant_a.id,
            entrada_padron_id=entry.id,
            materia_id=materia.id,
            actividad="TP",
            nota_numerica=50.00,
            origen="Invalido",
        )
        db_session.add(cal)
        with pytest.raises(sa.exc.IntegrityError):
            await db_session.commit()
        await db_session.rollback()

    async def test_soft_delete(self, db_session, tenant_a):
        entry, materia, _ = await _seed_data(db_session, tenant_a)
        cal = Calificacion(
            tenant_id=tenant_a.id,
            entrada_padron_id=entry.id,
            materia_id=materia.id,
            actividad="TP",
            nota_numerica=50.00,
            origen="Manual",
        )
        db_session.add(cal)
        await db_session.commit()
        await db_session.refresh(cal)

        cal.deleted_at = sa.func.now()
        await db_session.commit()

        stmt = select(Calificacion).where(
            Calificacion.id == cal.id,
            Calificacion.deleted_at.is_(None),
        )
        result = await db_session.execute(stmt)
        assert result.scalar_one_or_none() is None

    async def test_create_with_both_notas(self, db_session, tenant_a):
        entry, materia, _ = await _seed_data(db_session, tenant_a)
        cal = Calificacion(
            tenant_id=tenant_a.id,
            entrada_padron_id=entry.id,
            materia_id=materia.id,
            actividad="Parcial",
            nota_numerica=70.00,
            nota_textual="Bueno",
            origen="Importado",
        )
        db_session.add(cal)
        await db_session.commit()
        await db_session.refresh(cal)
        assert cal.nota_numerica == 70.00
        assert cal.nota_textual == "Bueno"


@pytest.mark.needs_db
class TestUmbralMateriaModel:
    async def test_create_with_defaults(self, db_session, tenant_a):
        _, materia, user = await _seed_data(db_session, tenant_a)
        asign = await _seed_asignacion(db_session, tenant_a, materia, user)
        umbral = UmbralMateria(
            tenant_id=tenant_a.id,
            asignacion_id=asign.id,
            materia_id=materia.id,
        )
        db_session.add(umbral)
        await db_session.commit()
        await db_session.refresh(umbral)
        assert umbral.umbral_pct == 60
        assert "Satisfactorio" in umbral.valores_aprobatorios
        assert "Supera lo esperado" in umbral.valores_aprobatorios

    async def test_create_with_custom_values(self, db_session, tenant_a):
        _, materia, user = await _seed_data(db_session, tenant_a)
        asign = await _seed_asignacion(db_session, tenant_a, materia, user)
        umbral = UmbralMateria(
            tenant_id=tenant_a.id,
            asignacion_id=asign.id,
            materia_id=materia.id,
            umbral_pct=70,
            valores_aprobatorios=["Aprobado", "Excelente"],
        )
        db_session.add(umbral)
        await db_session.commit()
        await db_session.refresh(umbral)
        assert umbral.umbral_pct == 70
        assert umbral.valores_aprobatorios == ["Aprobado", "Excelente"]

    async def test_unique_constraint_violation(self, db_session, tenant_a):
        _, materia, user = await _seed_data(db_session, tenant_a)
        asign = await _seed_asignacion(db_session, tenant_a, materia, user)
        umbral1 = UmbralMateria(
            tenant_id=tenant_a.id,
            asignacion_id=asign.id,
            materia_id=materia.id,
        )
        db_session.add(umbral1)
        await db_session.commit()

        umbral2 = UmbralMateria(
            tenant_id=tenant_a.id,
            asignacion_id=asign.id,
            materia_id=materia.id,
        )
        db_session.add(umbral2)
        with pytest.raises(sa.exc.IntegrityError):
            await db_session.commit()
        await db_session.rollback()

    async def test_soft_delete(self, db_session, tenant_a):
        _, materia, user = await _seed_data(db_session, tenant_a)
        asign = await _seed_asignacion(db_session, tenant_a, materia, user)
        umbral = UmbralMateria(
            tenant_id=tenant_a.id,
            asignacion_id=asign.id,
            materia_id=materia.id,
        )
        db_session.add(umbral)
        await db_session.commit()
        await db_session.refresh(umbral)

        umbral.deleted_at = sa.func.now()
        await db_session.commit()

        stmt = select(UmbralMateria).where(
            UmbralMateria.id == umbral.id,
            UmbralMateria.deleted_at.is_(None),
        )
        result = await db_session.execute(stmt)
        assert result.scalar_one_or_none() is None


async def _seed_data(db_session, tenant):
    carrera = Carrera(codigo="CARR-10", nombre="CarreraC10", tenant_id=tenant.id)
    db_session.add(carrera)
    await db_session.flush()
    materia = Materia(codigo="MAT-10", nombre="MateriaC10", tenant_id=tenant.id)
    db_session.add(materia)
    await db_session.flush()
    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="2026-C", anio=2026,
        vig_desde=date(2026, 1, 1),
        tenant_id=tenant.id, activa=True,
    )
    db_session.add(cohorte)
    await db_session.flush()
    user = User(
        email="testuser10@test.com", password_hash=hash_password("pass123!"),
        nombre="Test", apellidos="User10", tenant_id=tenant.id,
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
        version_id=version.id, nombre="Juan", apellidos="Perez",
    )
    db_session.add(entrada)
    await db_session.commit()
    await db_session.refresh(materia)
    await db_session.refresh(entrada)
    await db_session.refresh(user)
    return entrada, materia, user


async def _seed_asignacion(db_session, tenant, materia, user):
    rol = Rol(nombre="PROFESOR_C10", descripcion="Profesor C10", tenant_id=tenant.id)
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
