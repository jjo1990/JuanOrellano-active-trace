"""Tests de integración HTTP para el router de comunicaciones (C-12)."""

import uuid
from datetime import date, datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from asgi_lifespan import LifespanManager

from app.core.config import Settings
from app.main import create_app
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.comunicacion import Comunicacion
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.permiso import Permiso
from app.models.rol import Rol
from app.models.rol_permiso import RolPermiso
from app.models.user import User
from app.models.usuario_rol import UsuarioRol
from app.models.version_padron import VersionPadron
from app.core.security import create_access_token, hash_password


async def _seed_rbac_permisos(db_session, tenant, user, permiso_codigos: list[str]):
    rol = Rol(nombre=f"ROL_{permiso_codigos[0]}", descripcion="Test rol", tenant_id=tenant.id)
    db_session.add(rol)
    await db_session.flush()

    for codigo in permiso_codigos:
        perm = Permiso(
            codigo=codigo, descripcion=f"Permiso {codigo}", modulo=codigo.split(":")[0],
        )
        db_session.add(perm)
        await db_session.flush()

        rp = RolPermiso(rol_id=rol.id, permiso_id=perm.id, tenant_id=tenant.id)
        db_session.add(rp)
        await db_session.flush()

    ahora = datetime.now(timezone.utc)
    ur = UsuarioRol(
        user_id=user.id, rol_id=rol.id, tenant_id=tenant.id,
        fecha_desde=ahora - date.resolution,
    )
    db_session.add(ur)
    await db_session.commit()

    return rol


def _make_auth_headers(user_id: uuid.UUID, tenant_id: uuid.UUID) -> dict:
    token = create_access_token(user_id=user_id, tenant_id=tenant_id)
    return {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": str(tenant_id),
    }


@pytest.mark.needs_db
class TestComunicacionesRouter:
    async def test_preview_200_con_datos(self, async_client, tenant_a, db_session):
        user = User(
            email="rt1@test.com", password_hash=hash_password("pass123!"),
            nombre="RT1", apellidos="Test", tenant_id=tenant_a.id,
        )
        db_session.add(user)
        await db_session.flush()
        await _seed_rbac_permisos(db_session, tenant_a, user, ["comunicacion:enviar"])

        headers = _make_auth_headers(user.id, tenant_a.id)

        response = await async_client.post(
            "/api/comunicaciones/preview",
            json={
                "template": "Hola {{nombre}}",
                "alumno_ids": [str(uuid.uuid4())],
                "materia_id": str(uuid.uuid4()),
            },
            headers=headers,
        )
        assert response.status_code == 200

    async def test_enviar_sin_permiso_retorna_403(self, async_client, tenant_a, db_session):
        user = User(
            email="rt2@test.com", password_hash=hash_password("pass123!"),
            nombre="RT2", apellidos="Test", tenant_id=tenant_a.id,
        )
        db_session.add(user)
        await db_session.commit()

        headers = _make_auth_headers(user.id, tenant_a.id)

        response = await async_client.post(
            "/api/comunicaciones/enviar",
            json={
                "template": "Test",
                "alumno_ids": [str(uuid.uuid4())],
                "materia_id": str(uuid.uuid4()),
                "asunto": "Test",
            },
            headers=headers,
        )
        assert response.status_code == 403

    async def test_aprobar_sin_permiso_retorna_403(self, async_client, tenant_a, db_session):
        user = User(
            email="rt3@test.com", password_hash=hash_password("pass123!"),
            nombre="RT3", apellidos="Test", tenant_id=tenant_a.id,
        )
        db_session.add(user)
        await db_session.flush()
        await _seed_rbac_permisos(db_session, tenant_a, user, ["comunicacion:enviar"])

        headers = _make_auth_headers(user.id, tenant_a.id)

        response = await async_client.post(
            f"/api/comunicaciones/aprobar/{uuid.uuid4()}",
            headers=headers,
        )
        assert response.status_code == 403

    async def test_flujo_completo_preview_enviar_aprobar_consultar(
        self, async_client, tenant_a, db_session,
    ):
        user = User(
            email="rt4@test.com", password_hash=hash_password("pass123!"),
            nombre="RT4", apellidos="Test", tenant_id=tenant_a.id,
        )
        db_session.add(user)
        await db_session.flush()
        await _seed_rbac_permisos(
            db_session, tenant_a, user,
            ["comunicacion:enviar", "comunicacion:aprobar"],
        )

        carrera = Carrera(codigo="RT-CARR", nombre="RtCarr", tenant_id=tenant_a.id)
        db_session.add(carrera)
        await db_session.flush()
        materia = Materia(codigo="RT-MAT", nombre="RtMat", tenant_id=tenant_a.id)
        db_session.add(materia)
        await db_session.flush()
        cohorte = Cohorte(
            carrera_id=carrera.id, nombre="2026-R", anio=2026,
            vig_desde=date(2026, 1, 1), tenant_id=tenant_a.id, activa=True,
        )
        db_session.add(cohorte)
        await db_session.flush()
        version = VersionPadron(
            tenant_id=tenant_a.id,
            materia_id=materia.id, cohorte_id=cohorte.id,
            cargado_por=user.id, activa=True,
        )
        db_session.add(version)
        await db_session.flush()
        entrada = EntradaPadron(
            tenant_id=tenant_a.id,
            version_id=version.id,
            nombre="Juan", apellidos="Perez",
            email="juan@test.com",
        )
        db_session.add(entrada)
        await db_session.commit()

        headers = _make_auth_headers(user.id, tenant_a.id)

        preview_response = await async_client.post(
            "/api/comunicaciones/preview",
            json={
                "template": "Hola {{nombre}}, materia: {{materia}}",
                "alumno_ids": [str(entrada.id)],
                "materia_id": str(materia.id),
            },
            headers=headers,
        )
        assert preview_response.status_code == 200
        preview_data = preview_response.json()
        assert len(preview_data["previews"]) == 1

        enviar_response = await async_client.post(
            "/api/comunicaciones/enviar",
            json={
                "template": "Hola {{nombre}}, materia: {{materia}}",
                "alumno_ids": [str(entrada.id)],
                "materia_id": str(materia.id),
                "asunto": "Recordatorio {{materia}}",
            },
            headers=headers,
        )
        assert enviar_response.status_code == 200
        envio_data = enviar_response.json()
        lote_id = envio_data["lote_id"]

        aprobar_response = await async_client.post(
            f"/api/comunicaciones/aprobar/{lote_id}",
            headers=headers,
        )
        assert aprobar_response.status_code == 200

        status_response = await async_client.get(
            f"/api/comunicaciones/lote/{lote_id}",
            headers=headers,
        )
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["lote_id"] == lote_id
        assert len(status_data["comunicaciones"]) == 1

    async def test_get_materia_200(self, async_client, tenant_a, db_session):
        user = User(
            email="rt5@test.com", password_hash=hash_password("pass123!"),
            nombre="RT5", apellidos="Test", tenant_id=tenant_a.id,
        )
        db_session.add(user)
        await db_session.flush()
        await _seed_rbac_permisos(db_session, tenant_a, user, ["comunicacion:enviar"])

        headers = _make_auth_headers(user.id, tenant_a.id)

        response = await async_client.get(
            f"/api/comunicaciones/materia/{uuid.uuid4()}",
            headers=headers,
        )
        assert response.status_code == 200

    async def test_cancelar_200(self, async_client, tenant_a, db_session):
        user = User(
            email="rt6@test.com", password_hash=hash_password("pass123!"),
            nombre="RT6", apellidos="Test", tenant_id=tenant_a.id,
        )
        db_session.add(user)
        await db_session.flush()
        await _seed_rbac_permisos(db_session, tenant_a, user, ["comunicacion:enviar"])

        carrera = Carrera(codigo="RT6-C", nombre="Rt6Carr", tenant_id=tenant_a.id)
        db_session.add(carrera)
        await db_session.flush()
        materia = Materia(codigo="RT6-M", nombre="Rt6Mat", tenant_id=tenant_a.id)
        db_session.add(materia)
        await db_session.flush()
        cohorte = Cohorte(
            carrera_id=carrera.id, nombre="2026-6", anio=2026,
            vig_desde=date(2026, 1, 1), tenant_id=tenant_a.id, activa=True,
        )
        db_session.add(cohorte)
        await db_session.flush()
        version = VersionPadron(
            tenant_id=tenant_a.id,
            materia_id=materia.id, cohorte_id=cohorte.id,
            cargado_por=user.id, activa=True,
        )
        db_session.add(version)
        await db_session.flush()
        entrada = EntradaPadron(
            tenant_id=tenant_a.id,
            version_id=version.id,
            nombre="X", apellidos="Y", email="x@test.com",
        )
        db_session.add(entrada)
        await db_session.commit()

        headers = _make_auth_headers(user.id, tenant_a.id)

        enviar_response = await async_client.post(
            "/api/comunicaciones/enviar",
            json={
                "template": "Hola {{nombre}}",
                "alumno_ids": [str(entrada.id)],
                "materia_id": str(materia.id),
                "asunto": "Test",
            },
            headers=headers,
        )
        assert enviar_response.status_code == 200
        lote_id = enviar_response.json()["lote_id"]

        status_resp = await async_client.get(
            f"/api/comunicaciones/lote/{lote_id}",
            headers=headers,
        )
        com_id = status_resp.json()["comunicaciones"][0]["id"]

        cancel_response = await async_client.post(
            f"/api/comunicaciones/cancelar/{com_id}",
            json={"motivo": "Error en datos"},
            headers=headers,
        )
        assert cancel_response.status_code == 200
        assert cancel_response.json()["estado"] == "Cancelado"
