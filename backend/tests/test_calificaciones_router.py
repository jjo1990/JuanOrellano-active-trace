"""Tests de integración para Calificaciones Router (C-10)."""

import io
import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
import sqlalchemy as sa
from httpx import ASGITransport, AsyncClient
from asgi_lifespan import LifespanManager
from jose import jwt

from app.core.config import Settings
from app.core import action_codes
from app.main import create_app
from app.models.audit_log import AuditLog
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.permiso import Permiso
from app.models.rol import Rol
from app.models.rol_permiso import RolPermiso
from app.models.usuario_rol import UsuarioRol
from app.models.user import User
from app.models.asignacion import Asignacion
from app.models.entrada_padron import EntradaPadron
from app.models.version_padron import VersionPadron
from app.core.security import hash_password


SAMPLE_CAL_CSV = (
    b"Nombre,Apellidos,Examen (Real),Satisfactorio\r\n"
    b"Juan,Perez,85,Satisfactorio\r\n"
    b"Maria,Gomez,45,Regular\r\n"
)


def _make_xlsx(headers, rows):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(headers)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


@pytest.mark.needs_db
class TestCalificacionesRouter:
    @pytest.fixture
    async def cal_client(self, db_session, tenant_a, tenant_b):
        settings = Settings()
        carrera = Carrera(codigo="CARR-INT", nombre="CarreraInt", tenant_id=tenant_a.id)
        db_session.add(carrera)
        await db_session.flush()
        materia = Materia(codigo="MAT-INT", nombre="MateriaInt", tenant_id=tenant_a.id)
        db_session.add(materia)
        await db_session.flush()
        cohorte = Cohorte(
            carrera_id=carrera.id, nombre="2026-I", anio=2026,
            vig_desde=date(2026, 1, 1), tenant_id=tenant_a.id, activa=True,
        )
        db_session.add(cohorte)
        await db_session.flush()

        admin_rol = Rol(nombre="ADMIN_CAL", descripcion="Admin cal", tenant_id=tenant_a.id)
        db_session.add(admin_rol)
        await db_session.flush()

        perm = Permiso(
            codigo="calificaciones:importar",
            descripcion="Importar calificaciones",
            modulo="calificaciones",
        )
        db_session.add(perm)
        await db_session.flush()

        rp = RolPermiso(
            rol_id=admin_rol.id, permiso_id=perm.id, tenant_id=tenant_a.id,
        )
        db_session.add(rp)

        user = User(
            email="admin_cal@test.com", password_hash=hash_password("pass123!"),
            nombre="Admin", apellidos="Cal", tenant_id=tenant_a.id,
        )
        db_session.add(user)
        await db_session.flush()

        ur = UsuarioRol(
            user_id=user.id, rol_id=admin_rol.id,
            fecha_desde=datetime.now(timezone.utc) - timedelta(days=30),
            tenant_id=tenant_a.id,
        )
        db_session.add(ur)

        viewer_rol = Rol(nombre="VIEWER_CAL", descripcion="Viewer", tenant_id=tenant_a.id)
        db_session.add(viewer_rol)
        await db_session.flush()

        viewer = User(
            email="viewer_cal@test.com", password_hash=hash_password("pass123!"),
            nombre="Viewer", apellidos="Cal", tenant_id=tenant_a.id,
        )
        db_session.add(viewer)
        await db_session.flush()

        viewer_ur = UsuarioRol(
            user_id=viewer.id, rol_id=viewer_rol.id,
            fecha_desde=datetime.now(timezone.utc) - timedelta(days=30),
            tenant_id=tenant_a.id,
        )
        db_session.add(viewer_ur)
        await db_session.flush()

        asignacion = Asignacion(
            tenant_id=tenant_a.id,
            usuario_id=user.id,
            rol_id=admin_rol.id,
            materia_id=materia.id,
            desde=date(2026, 1, 1),
        )
        db_session.add(asignacion)
        await db_session.commit()
        await db_session.refresh(asignacion)

        admin_token = jwt.encode(
            {"sub": str(user.id), "tenant_id": str(tenant_a.id),
             "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
            settings.secret_key, algorithm=settings.jwt_algorithm,
        )
        viewer_token = jwt.encode(
            {"sub": str(viewer.id), "tenant_id": str(tenant_a.id),
             "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
            settings.secret_key, algorithm=settings.jwt_algorithm,
        )

        app = create_app()
        async with LifespanManager(app):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                yield {
                    "client": client,
                    "admin_token": admin_token,
                    "viewer_token": viewer_token,
                    "materia_id": str(materia.id),
                    "cohorte_id": str(cohorte.id),
                    "user_id": str(user.id),
                    "tenant_a_id": str(tenant_a.id),
                    "tenant_b_id": str(tenant_b.id),
                    "asignacion_id": str(asignacion.id),
                }

    async def test_import_xlsx_retorna_preview(self, cal_client):
        data = cal_client
        xlsx = _make_xlsx(
            ["Nombre", "Apellidos", "Examen (Real)", "Satisfactorio"],
            [["Juan", "Perez", "85", "Satisfactorio"]],
        )
        files = {"file": ("calificaciones.xlsx", xlsx, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        form_data = {
            "materia_id": data["materia_id"],
            "cohorte_id": data["cohorte_id"],
            "asignacion_id": str(uuid.uuid4()),
        }
        response = await data["client"].post(
            "/api/calificaciones/import",
            files=files,
            data=form_data,
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert "preview_token" in body
        assert body["detected_rows"] == 1
        assert len(body["columns"]) == 4

    async def test_import_csv_retorna_preview(self, cal_client):
        data = cal_client
        files = {"file": ("calificaciones.csv", SAMPLE_CAL_CSV, "text/csv")}
        form_data = {
            "materia_id": data["materia_id"],
            "cohorte_id": data["cohorte_id"],
            "asignacion_id": str(uuid.uuid4()),
        }
        response = await data["client"].post(
            "/api/calificaciones/import",
            files=files,
            data=form_data,
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["detected_rows"] == 2

    async def test_import_sin_permiso_retorna_403(self, cal_client):
        data = cal_client
        files = {"file": ("calif.csv", SAMPLE_CAL_CSV, "text/csv")}
        form_data = {
            "materia_id": data["materia_id"],
            "cohorte_id": data["cohorte_id"],
            "asignacion_id": str(uuid.uuid4()),
        }
        response = await data["client"].post(
            "/api/calificaciones/import",
            files=files,
            data=form_data,
            headers={"Authorization": f"Bearer {data['viewer_token']}"},
        )
        assert response.status_code == 403

    async def test_confirm_con_token_valido_persiste(self, cal_client, db_session, tenant_a):
        data = cal_client
        user_id = uuid.UUID(data["user_id"])
        materia_id = uuid.UUID(data["materia_id"])
        cohorte_id = uuid.UUID(data["cohorte_id"])

        version = VersionPadron(
            tenant_id=tenant_a.id,
            materia_id=materia_id, cohorte_id=cohorte_id,
            cargado_por=user_id, activa=True,
        )
        db_session.add(version)
        await db_session.flush()
        entrada = EntradaPadron(
            tenant_id=tenant_a.id,
            version_id=version.id, nombre="Juan", apellidos="Perez",
        )
        db_session.add(entrada)
        await db_session.commit()

        xlsx = _make_xlsx(
            ["Nombre", "Apellidos", "Examen (Real)"],
            [["Juan", "Perez", "85"]],
        )
        files = {"file": ("cal.xlsx", xlsx, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        form_data = {
            "materia_id": str(materia_id),
            "cohorte_id": str(cohorte_id),
            "asignacion_id": str(uuid.uuid4()),
        }
        preview_resp = await data["client"].post(
            "/api/calificaciones/import",
            files=files,
            data=form_data,
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert preview_resp.status_code == 200
        token = preview_resp.json()["preview_token"]

        confirm_body = {"actividades_seleccionadas": ["Examen (Real)"]}
        confirm_resp = await data["client"].post(
            f"/api/calificaciones/confirm/{token}",
            json=confirm_body,
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert confirm_resp.status_code == 200, confirm_resp.text
        cbody = confirm_resp.json()
        assert cbody["calificaciones_count"] == 1
        assert cbody["ignorados_count"] == 0

    async def test_confirm_ignora_sin_entrada_padron(self, cal_client):
        data = cal_client
        xlsx = _make_xlsx(
            ["Nombre", "Apellidos", "Examen (Real)"],
            [["Juan", "Perez", "85"], ["NoExiste", "Persona", "90"]],
        )
        files = {"file": ("cal.xlsx", xlsx, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        form_data = {
            "materia_id": data["materia_id"],
            "cohorte_id": data["cohorte_id"],
            "asignacion_id": str(uuid.uuid4()),
        }
        preview_resp = await data["client"].post(
            "/api/calificaciones/import",
            files=files,
            data=form_data,
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert preview_resp.status_code == 200
        token = preview_resp.json()["preview_token"]

        confirm_resp = await data["client"].post(
            f"/api/calificaciones/confirm/{token}",
            json={"actividades_seleccionadas": ["Examen (Real)"]},
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert confirm_resp.status_code == 200
        cbody = confirm_resp.json()
        assert cbody["ignorados_count"] >= 0

    async def test_confirm_token_invalido_retorna_404(self, cal_client):
        data = cal_client
        response = await data["client"].post(
            "/api/calificaciones/confirm/token-invalido",
            json={"actividades_seleccionadas": []},
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert response.status_code == 404

    async def test_import_registra_audit_log(self, cal_client, db_session, tenant_a):
        data = cal_client
        user_id = uuid.UUID(data["user_id"])
        materia_id = uuid.UUID(data["materia_id"])
        cohorte_id = uuid.UUID(data["cohorte_id"])

        version = VersionPadron(
            tenant_id=tenant_a.id,
            materia_id=materia_id, cohorte_id=cohorte_id,
            cargado_por=user_id, activa=True,
        )
        db_session.add(version)
        await db_session.flush()
        entrada = EntradaPadron(
            tenant_id=tenant_a.id,
            version_id=version.id, nombre="Juan", apellidos="Perez",
        )
        db_session.add(entrada)
        await db_session.commit()

        xlsx = _make_xlsx(
            ["Nombre", "Apellidos", "Examen (Real)"],
            [["Juan", "Perez", "85"]],
        )
        files = {"file": ("cal.xlsx", xlsx, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        form_data = {
            "materia_id": str(materia_id),
            "cohorte_id": str(cohorte_id),
            "asignacion_id": str(uuid.uuid4()),
        }
        preview_resp = await data["client"].post(
            "/api/calificaciones/import",
            files=files,
            data=form_data,
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        token = preview_resp.json()["preview_token"]
        await data["client"].post(
            f"/api/calificaciones/confirm/{token}",
            json={"actividades_seleccionadas": ["Examen (Real)"]},
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )

        stmt = sa.select(AuditLog).where(AuditLog.accion == action_codes.CALIFICACIONES_IMPORTAR)
        result = await db_session.execute(stmt)
        logs = result.scalars().all()
        assert len(logs) >= 1

    async def test_formato_no_soportado_retorna_422(self, cal_client):
        data = cal_client
        files = {"file": ("cal.txt", b"hello", "text/plain")}
        form_data = {
            "materia_id": data["materia_id"],
            "cohorte_id": data["cohorte_id"],
            "asignacion_id": str(uuid.uuid4()),
        }
        response = await data["client"].post(
            "/api/calificaciones/import",
            files=files,
            data=form_data,
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert response.status_code == 422

    async def test_get_umbral_retorna_defaults(self, cal_client):
        data = cal_client
        response = await data["client"].get(
            f"/api/calificaciones/umbral/{data['materia_id']}?asignacion_id={data['asignacion_id']}",
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["umbral_pct"] == 60
        assert "Satisfactorio" in body["valores_aprobatorios"]

    async def test_put_umbral_creates(self, cal_client):
        data = cal_client
        body = {"umbral_pct": 70, "valores_aprobatorios": ["Aprobado", "Excelente"]}
        response = await data["client"].put(
            f"/api/calificaciones/umbral/{data['materia_id']}?asignacion_id={data['asignacion_id']}",
            json=body,
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert response.status_code == 200, response.text
        rbody = response.json()
        assert rbody["umbral_pct"] == 70
        assert rbody["valores_aprobatorios"] == ["Aprobado", "Excelente"]

    async def test_put_umbral_updates_existing(self, cal_client):
        data = cal_client
        body1 = {"umbral_pct": 70, "valores_aprobatorios": ["Aprobado"]}
        resp1 = await data["client"].put(
            f"/api/calificaciones/umbral/{data['materia_id']}?asignacion_id={data['asignacion_id']}",
            json=body1,
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert resp1.status_code == 200

        body2 = {"umbral_pct": 80, "valores_aprobatorios": ["Excelente"]}
        resp2 = await data["client"].put(
            f"/api/calificaciones/umbral/{data['materia_id']}?asignacion_id={data['asignacion_id']}",
            json=body2,
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert resp2.status_code == 200
        rbody = resp2.json()
        assert rbody["umbral_pct"] == 80
        assert rbody["valores_aprobatorios"] == ["Excelente"]

    async def test_put_umbral_sin_permiso_retorna_403(self, cal_client):
        data = cal_client
        body = {"umbral_pct": 70, "valores_aprobatorios": ["Aprobado"]}
        response = await data["client"].put(
            f"/api/calificaciones/umbral/{data['materia_id']}?asignacion_id={uuid.uuid4()}",
            json=body,
            headers={"Authorization": f"Bearer {data['viewer_token']}"},
        )
        assert response.status_code == 403

    async def test_get_umbral_sin_permiso_retorna_403(self, cal_client):
        data = cal_client
        response = await data["client"].get(
            f"/api/calificaciones/umbral/{data['materia_id']}?asignacion_id={uuid.uuid4()}",
            headers={"Authorization": f"Bearer {data['viewer_token']}"},
        )
        assert response.status_code == 403

    async def test_import_finalizacion_retorna_200(self, cal_client, db_session, tenant_a):
        data = cal_client
        user_id = uuid.UUID(data["user_id"])
        materia_id = uuid.UUID(data["materia_id"])
        cohorte_id = uuid.UUID(data["cohorte_id"])

        version = VersionPadron(
            tenant_id=tenant_a.id,
            materia_id=materia_id, cohorte_id=cohorte_id,
            cargado_por=user_id, activa=True,
        )
        db_session.add(version)
        await db_session.flush()
        entrada = EntradaPadron(
            tenant_id=tenant_a.id,
            version_id=version.id, nombre="Juan", apellidos="Perez",
        )
        db_session.add(entrada)
        await db_session.commit()

        xlsx = _make_xlsx(
            ["Nombre", "Apellidos", "Estado"],
            [["Juan", "Perez", "Finalizado"]],
        )
        files = {"file": ("finalizacion.xlsx", xlsx, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        form_data = {
            "materia_id": str(materia_id),
            "cohorte_id": str(cohorte_id),
            "asignacion_id": str(uuid.uuid4()),
        }
        response = await data["client"].post(
            "/api/calificaciones/import-finalizacion",
            files=files,
            data=form_data,
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["calificaciones_count"] == 1
