import uuid
from datetime import date

import pytest

from app.models.asignacion import Asignacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.liquidacion import EstadoLiquidacion
from app.models.materia import Materia
from app.models.rol import Rol
from app.models.salario_base import RolSalario, SalarioBase
from app.models.salario_plus import SalarioPlus
from app.models.user import User
from app.repositories.liquidacion_repository import LiquidacionRepository
from app.services.liquidacion_service import LiquidacionService


@pytest.fixture
async def seed_liquidacion_service(db_session, tenant_a):
    user1 = User(
        email="ls1@test.com", password_hash="hash",
        nombre="Profesor", apellidos="Uno", tenant_id=tenant_a.id,
        legajo="L-LS-1", cbu_encrypted="enc_cbu_12345",
    )
    user2 = User(
        email="ls2@test.com", password_hash="hash",
        nombre="Sin", apellidos="CBU", tenant_id=tenant_a.id,
        legajo="L-LS-2",
    )
    user3 = User(
        email="ls3@test.com", password_hash="hash",
        nombre="Facturante", apellidos="Tres", tenant_id=tenant_a.id,
        legajo="L-LS-3", cbu_encrypted="enc_cbu_67890", facturador=True,
    )
    user_nexo = User(
        email="ls_nexo@test.com", password_hash="hash",
        nombre="Nexo", apellidos="Test", tenant_id=tenant_a.id,
        legajo="L-LS-NEXO", cbu_encrypted="enc_cbu_nexo",
    )
    db_session.add_all([user1, user2, user3, user_nexo])
    await db_session.flush()

    rol_prof = Rol(nombre="PROFESOR", descripcion="Profesor", tenant_id=tenant_a.id)
    rol_tutor = Rol(nombre="TUTOR", descripcion="Tutor", tenant_id=tenant_a.id)
    rol_nexo = Rol(nombre="NEXO", descripcion="Nexo", tenant_id=tenant_a.id)
    db_session.add_all([rol_prof, rol_tutor, rol_nexo])
    await db_session.flush()

    materia_prog = Materia(
        codigo="PROG_I", nombre="Programación I", activa=True,
        grupo_plus="PROG", tenant_id=tenant_a.id,
    )
    materia_bd = Materia(
        codigo="BD_I", nombre="Base de Datos I", activa=True,
        grupo_plus="BD", tenant_id=tenant_a.id,
    )
    materia_sin = Materia(
        codigo="MAT_I", nombre="Matemática I", activa=True,
        grupo_plus=None, tenant_id=tenant_a.id,
    )
    db_session.add_all([materia_prog, materia_bd, materia_sin])
    await db_session.flush()

    carrera = Carrera(codigo="CAR_LS", nombre="Carrera LS", activa=True, tenant_id=tenant_a.id)
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="COH_LS", anio=2026,
        vig_desde=date(2026, 1, 1), activa=True, tenant_id=tenant_a.id,
    )
    db_session.add(cohorte)
    await db_session.flush()

    asig1 = Asignacion(
        usuario_id=user1.id, rol_id=rol_prof.id, materia_id=materia_prog.id,
        cohorte_id=cohorte.id, comisiones=["A", "B"],
        desde=date(2026, 1, 1), hasta=None, tenant_id=tenant_a.id,
    )
    asig2 = Asignacion(
        usuario_id=user1.id, rol_id=rol_prof.id, materia_id=materia_bd.id,
        cohorte_id=cohorte.id, comisiones=["C"],
        desde=date(2026, 1, 1), hasta=None, tenant_id=tenant_a.id,
    )
    asig3 = Asignacion(
        usuario_id=user1.id, rol_id=rol_tutor.id, materia_id=materia_sin.id,
        cohorte_id=cohorte.id, comisiones=["D"],
        desde=date(2026, 1, 1), hasta=None, tenant_id=tenant_a.id,
    )
    asig_sin_cbu = Asignacion(
        usuario_id=user2.id, rol_id=rol_prof.id, materia_id=materia_prog.id,
        cohorte_id=cohorte.id, comisiones=["E"],
        desde=date(2026, 1, 1), hasta=None, tenant_id=tenant_a.id,
    )
    asig_facturante = Asignacion(
        usuario_id=user3.id, rol_id=rol_prof.id, materia_id=materia_prog.id,
        cohorte_id=cohorte.id, comisiones=["F"],
        desde=date(2026, 1, 1), hasta=None, tenant_id=tenant_a.id,
    )
    asig_nexo = Asignacion(
        usuario_id=user_nexo.id, rol_id=rol_nexo.id, materia_id=materia_prog.id,
        cohorte_id=cohorte.id, comisiones=["N"],
        desde=date(2026, 1, 1), hasta=None, tenant_id=tenant_a.id,
    )
    db_session.add_all([asig1, asig2, asig3, asig_sin_cbu, asig_facturante, asig_nexo])
    await db_session.flush()

    sb_prof = SalarioBase(
        tenant_id=tenant_a.id, rol=RolSalario.PROFESOR, monto=80000.00,
        desde=date(2026, 1, 1), hasta=None,
    )
    sb_tutor = SalarioBase(
        tenant_id=tenant_a.id, rol=RolSalario.TUTOR, monto=50000.00,
        desde=date(2026, 1, 1), hasta=None,
    )
    sb_nexo = SalarioBase(
        tenant_id=tenant_a.id, rol=RolSalario.NEXO, monto=60000.00,
        desde=date(2026, 1, 1), hasta=None,
    )
    db_session.add_all([sb_prof, sb_tutor, sb_nexo])

    sp_prog = SalarioPlus(
        tenant_id=tenant_a.id, grupo="PROG", rol=RolSalario.PROFESOR,
        descripcion="Plus Prog", monto=15000.00,
        desde=date(2026, 1, 1), hasta=None,
    )
    sp_bd = SalarioPlus(
        tenant_id=tenant_a.id, grupo="BD", rol=RolSalario.PROFESOR,
        descripcion="Plus BD", monto=10000.00,
        desde=date(2026, 1, 1), hasta=None,
    )
    sp_nexo = SalarioPlus(
        tenant_id=tenant_a.id, grupo="PROG", rol=RolSalario.NEXO,
        descripcion="Plus Nexo", monto=5000.00,
        desde=date(2026, 1, 1), hasta=None,
    )
    db_session.add_all([sp_prog, sp_bd, sp_nexo])
    await db_session.commit()

    return {
        "tenant_a_id": tenant_a.id,
        "cohorte_id": cohorte.id,
        "user1_id": user1.id,
        "user2_id": user2.id,
        "user3_id": user3.id,
        "user_nexo_id": user_nexo.id,
        "materia_prog_id": materia_prog.id,
        "materia_bd_id": materia_bd.id,
        "materia_sin_id": materia_sin.id,
    }


@pytest.mark.needs_db
class TestLiquidacionServiceCalcular:
    async def test_calculo_exitoso_docente_multi_rol(self, db_session, seed_liquidacion_service):
        d = seed_liquidacion_service
        svc = LiquidacionService(db_session, d["tenant_a_id"])
        result = await svc.calcular(d["cohorte_id"], "2026-06", d["user1_id"])

        assert len(result.advertencias) > 0
        user1_liqs = [l for l in result.liquidaciones if l.usuario_id == d["user1_id"]]
        assert len(user1_liqs) == 1
        liq = user1_liqs[0]
        assert liq.monto_base == 80000.0
        plus_esperado = 15000.0 * 2 + 10000.0 * 1
        assert liq.monto_plus == plus_esperado
        assert liq.total == 80000.0 + plus_esperado
        assert not liq.es_nexo
        assert not liq.excluido_por_factura

    async def test_docente_sin_cbu_omitido(self, db_session, seed_liquidacion_service):
        d = seed_liquidacion_service
        svc = LiquidacionService(db_session, d["tenant_a_id"])
        result = await svc.calcular(d["cohorte_id"], "2026-06", d["user1_id"])

        warnings = [a for a in result.advertencias if a["usuario_id"] == str(d["user2_id"])]
        assert len(warnings) == 1
        assert "CBU" in warnings[0]["motivo"]
        user2_liqs = [l for l in result.liquidaciones if l.usuario_id == d["user2_id"]]
        assert len(user2_liqs) == 0

    async def test_docente_facturante_excluido(self, db_session, seed_liquidacion_service):
        d = seed_liquidacion_service
        svc = LiquidacionService(db_session, d["tenant_a_id"])
        result = await svc.calcular(d["cohorte_id"], "2026-06", d["user1_id"])

        user3_liqs = [l for l in result.liquidaciones if l.usuario_id == d["user3_id"]]
        assert len(user3_liqs) == 1
        assert user3_liqs[0].excluido_por_factura is True

    async def test_docente_nexo_identificado(self, db_session, seed_liquidacion_service):
        d = seed_liquidacion_service
        svc = LiquidacionService(db_session, d["tenant_a_id"])
        result = await svc.calcular(d["cohorte_id"], "2026-06", d["user1_id"])

        nexo_liqs = [l for l in result.liquidaciones if l.usuario_id == d["user_nexo_id"]]
        assert len(nexo_liqs) == 1
        assert nexo_liqs[0].es_nexo is True

    async def test_segmentacion_contable(self, db_session, seed_liquidacion_service):
        d = seed_liquidacion_service
        svc = LiquidacionService(db_session, d["tenant_a_id"])
        await svc.calcular(d["cohorte_id"], "2026-06", d["user1_id"])
        await db_session.commit()

        result = await svc.listar_segmentado(d["cohorte_id"], "2026-06")
        assert len(result.general) >= 1
        assert result.total_sin_factura > 0


@pytest.mark.needs_db
class TestLiquidacionServiceCerrar:
    async def test_cierre_exitoso(self, db_session, seed_liquidacion_service):
        d = seed_liquidacion_service
        svc = LiquidacionService(db_session, d["tenant_a_id"])
        await svc.calcular(d["cohorte_id"], "2026-06", d["user1_id"])
        await db_session.commit()

        cerrar_svc = LiquidacionService(db_session, d["tenant_a_id"])
        result = await cerrar_svc.cerrar(d["cohorte_id"], "2026-06", d["user1_id"])
        assert result.cantidad_cerradas > 0

    async def test_cierre_sin_abiertas_rechazado(self, db_session, seed_liquidacion_service):
        d = seed_liquidacion_service
        svc = LiquidacionService(db_session, d["tenant_a_id"])
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await svc.cerrar(d["cohorte_id"], "2026-06", d["user1_id"])
        assert exc.value.status_code == 404

    async def test_recalcular_cerrada_rechazado(self, db_session, seed_liquidacion_service):
        d = seed_liquidacion_service
        svc = LiquidacionService(db_session, d["tenant_a_id"])
        result = await svc.calcular(d["cohorte_id"], "2026-06", d["user1_id"])
        await db_session.commit()

        liq_id = result.liquidaciones[0].id

        cerrar_svc = LiquidacionService(db_session, d["tenant_a_id"])
        await cerrar_svc.cerrar(d["cohorte_id"], "2026-06", d["user1_id"])
        await db_session.commit()

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await svc.recalcular(liq_id, d["user1_id"])
        assert exc.value.status_code == 409
