"""Tests para AuditoriaService (C-19)."""

import uuid
from datetime import date, datetime, timedelta, timezone

import pytest

from app.core import action_codes
from app.core.security import hash_password
from app.models.asignacion import Asignacion
from app.models.audit_log import AuditLog
from app.models.materia import Materia
from app.models.rol import Rol
from app.models.user import User
from app.schemas.auditoria import (
    LogFilterParams,
    LogListResponse,
    PanelFilterParams,
    PanelResponse,
)
from app.services.auditoria_service import AuditoriaService


async def _seed_service_data(db_session, tenant):
    user = User(
        email=f"svc_audit_{uuid.uuid4().hex[:6]}@test.com",
        password_hash=hash_password("pass123!"),
        nombre="Svc", apellidos="User",
        tenant_id=tenant.id,
    )
    db_session.add(user)

    materia = Materia(
        codigo=f"MAT-SVC-{uuid.uuid4().hex[:6]}",
        nombre="SvcMateria", tenant_id=tenant.id,
    )
    db_session.add(materia)
    await db_session.flush()

    now = datetime.now(timezone.utc)
    for i in range(5):
        db_session.add(AuditLog(
            tenant_id=tenant.id,
            actor_id=user.id,
            materia_id=materia.id,
            accion=action_codes.CALIFICACIONES_IMPORTAR,
            detalle={"count": i},
            filas_afectadas=i * 10,
            fecha_hora=now - timedelta(days=i),
        ))

    db_session.add(AuditLog(
        tenant_id=tenant.id,
        actor_id=user.id,
        materia_id=materia.id,
        accion="COMUNICACION_ENVIAR",
        detalle={"accion": "aprobar_lote", "lote_id": str(uuid.uuid4()), "afectadas": 5},
        fecha_hora=now - timedelta(days=1),
    ))

    await db_session.commit()
    return user, materia


async def _seed_coord_data(db_session, tenant, materia):
    coord = User(
        email=f"coord_audit_{uuid.uuid4().hex[:6]}@test.com",
        password_hash=hash_password("pass123!"),
        nombre="Coord", apellidos="SvcUser",
        tenant_id=tenant.id,
    )
    db_session.add(coord)

    otra_materia = Materia(
        codigo=f"MAT-OTRA-{uuid.uuid4().hex[:6]}",
        nombre="OtraMateria", tenant_id=tenant.id,
    )
    db_session.add(otra_materia)
    await db_session.flush()

    rol = Rol(nombre="COORDINADOR", descripcion="Coordinador", tenant_id=tenant.id)
    db_session.add(rol)
    await db_session.flush()

    hoy = date.today()
    db_session.add(Asignacion(
        tenant_id=tenant.id,
        usuario_id=coord.id,
        rol_id=rol.id,
        materia_id=materia.id,
        desde=hoy - timedelta(days=30),
    ))
    await db_session.commit()
    return coord, otra_materia


@pytest.mark.needs_db
class TestGetPanel:
    async def test_panel_retorna_cuatro_secciones(self, db_session, tenant_a):
        user, _ = await _seed_service_data(db_session, tenant_a)
        svc = AuditoriaService(db_session, tenant_a.id)
        result = await svc.get_panel(
            PanelFilterParams(limite=200), user.id,
        )
        assert isinstance(result, PanelResponse)
        assert isinstance(result.acciones_por_dia, list)
        assert isinstance(result.estado_comunicaciones, list)
        assert isinstance(result.interacciones_docente_materia, list)
        assert isinstance(result.ultimas_acciones, list)

    async def test_panel_ultimas_acciones_respeta_limite(self, db_session, tenant_a):
        user, _ = await _seed_service_data(db_session, tenant_a)
        svc = AuditoriaService(db_session, tenant_a.id)
        result = await svc.get_panel(
            PanelFilterParams(limite=2), user.id,
        )
        assert len(result.ultimas_acciones) <= 2

    async def test_panel_con_filtro_fecha(self, db_session, tenant_a):
        user, _ = await _seed_service_data(db_session, tenant_a)
        svc = AuditoriaService(db_session, tenant_a.id)
        desde = date.today() - timedelta(days=3)
        hasta = date.today() + timedelta(days=1)
        result = await svc.get_panel(
            PanelFilterParams(fecha_desde=desde, fecha_hasta=hasta, limite=10),
            user.id,
        )
        assert isinstance(result, PanelResponse)

    async def test_panel_con_scope_propio_coordinador(self, db_session, tenant_a):
        user, materia = await _seed_service_data(db_session, tenant_a)
        coord, otra_materia = await _seed_coord_data(db_session, tenant_a, materia)

        db_session.add(AuditLog(
            tenant_id=tenant_a.id,
            actor_id=user.id,
            materia_id=otra_materia.id,
            accion=action_codes.CALIFICACIONES_IMPORTAR,
            fecha_hora=datetime.now(timezone.utc),
        ))
        await db_session.commit()

        svc = AuditoriaService(db_session, tenant_a.id)
        result = await svc.get_panel(
            PanelFilterParams(limite=50), coord.id,
        )
        for item in result.ultimas_acciones:
            assert item.materia_id != otra_materia.id


@pytest.mark.needs_db
class TestGetLog:
    async def test_log_retorna_items(self, db_session, tenant_a):
        user, _ = await _seed_service_data(db_session, tenant_a)
        svc = AuditoriaService(db_session, tenant_a.id)
        result = await svc.get_log(
            LogFilterParams(limite=50), user.id,
        )
        assert isinstance(result, LogListResponse)
        assert len(result.items) > 0
        assert result.total > 0
        assert result.limite == 50
        assert result.offset == 0

    async def test_log_con_filtro_accion(self, db_session, tenant_a):
        user, _ = await _seed_service_data(db_session, tenant_a)
        svc = AuditoriaService(db_session, tenant_a.id)
        result = await svc.get_log(
            LogFilterParams(accion=action_codes.CALIFICACIONES_IMPORTAR, limite=50),
            user.id,
        )
        for item in result.items:
            assert item.accion == action_codes.CALIFICACIONES_IMPORTAR

    async def test_log_con_paginacion(self, db_session, tenant_a):
        user, _ = await _seed_service_data(db_session, tenant_a)
        svc = AuditoriaService(db_session, tenant_a.id)
        result = await svc.get_log(
            LogFilterParams(limite=2, offset=0), user.id,
        )
        assert len(result.items) <= 2

    async def test_log_con_filtro_usuario(self, db_session, tenant_a):
        user, _ = await _seed_service_data(db_session, tenant_a)
        other = User(
            email=f"other_log_{uuid.uuid4().hex[:6]}@test.com",
            password_hash=hash_password("pass123!"),
            nombre="Other", apellidos="Log",
            tenant_id=tenant_a.id,
        )
        db_session.add(other)
        await db_session.flush()

        db_session.add(AuditLog(
            tenant_id=tenant_a.id,
            actor_id=other.id,
            accion="PADRON_CARGAR",
            fecha_hora=datetime.now(timezone.utc),
        ))
        await db_session.commit()

        svc = AuditoriaService(db_session, tenant_a.id)
        result = await svc.get_log(
            LogFilterParams(usuario_id=other.id, limite=50), user.id,
        )
        for item in result.items:
            assert item.actor_id == other.id

    async def test_log_con_scope_propio_coordinador(self, db_session, tenant_a):
        user, materia = await _seed_service_data(db_session, tenant_a)
        coord, otra_materia = await _seed_coord_data(db_session, tenant_a, materia)

        db_session.add(AuditLog(
            tenant_id=tenant_a.id,
            actor_id=user.id,
            materia_id=otra_materia.id,
            accion=action_codes.PADRON_CARGAR,
            fecha_hora=datetime.now(timezone.utc),
        ))
        await db_session.commit()

        svc = AuditoriaService(db_session, tenant_a.id)
        result = await svc.get_log(
            LogFilterParams(limite=50), coord.id,
        )
        for item in result.items:
            assert item.materia_id != otra_materia.id

    async def test_log_sin_asignaciones_sin_scope(self, db_session, tenant_a):
        user, _ = await _seed_service_data(db_session, tenant_a)
        svc = AuditoriaService(db_session, tenant_a.id)
        result = await svc.get_log(
            LogFilterParams(limite=50), user.id,
        )
        assert result.total == 6
