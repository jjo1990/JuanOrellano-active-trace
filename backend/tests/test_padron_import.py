"""Tests para PadronService — import pipeline (C-09)."""

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
from app.models.version_padron import VersionPadron
from app.models.entrada_padron import EntradaPadron
from app.core.security import hash_password


SAMPLE_CSV = b"nombre,apellidos,email,comision,regional\nJuan,Perez,juan@test.com,A,BSAS\nMaria,Gomez,maria@test.com,B,CABA"
SAMPLE_XLSX_BYTES = None


def _make_xlsx():
    """Genera un xlsx válido en memoria con los mismos datos que SAMPLE_CSV."""
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(["nombre", "apellidos", "email", "comision", "regional"])
    ws.append(["Juan", "Perez", "juan@test.com", "A", "BSAS"])
    ws.append(["Maria", "Gomez", "maria@test.com", "B", "CABA"])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


@pytest.fixture
async def padron_import_fixtures(db_session, tenant_a):
    carrera = Carrera(codigo="CARR001", nombre="Ingeniería", tenant_id=tenant_a.id)
    db_session.add(carrera)
    await db_session.flush()
    materia = Materia(codigo="MAT101", nombre="Matemáticas", tenant_id=tenant_a.id)
    db_session.add(materia)
    await db_session.flush()
    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="2026-A", anio=2026,
        vig_desde=date(2026, 1, 1), tenant_id=tenant_a.id, activa=True,
    )
    db_session.add(cohorte)
    user = User(
        email="cargador@test.com", password_hash=hash_password("pass123!"),
        nombre="Cargador", apellidos="Test", tenant_id=tenant_a.id,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(materia)
    await db_session.refresh(cohorte)
    await db_session.refresh(user)
    return {
        "materia": materia,
        "cohorte": cohorte,
        "user": user,
        "tenant": tenant_a,
    }


@pytest.fixture
async def admin_padron_client_and_data(db_session, tenant_a, tenant_b):
    settings = Settings()
    carrera = Carrera(codigo="CARR002", nombre="Derecho", tenant_id=tenant_a.id)
    db_session.add(carrera)
    await db_session.flush()
    materia = Materia(codigo="MAT102", nombre="Física", tenant_id=tenant_a.id)
    db_session.add(materia)
    await db_session.flush()
    cohorte = Cohorte(
        carrera_id=carrera.id, nombre="2026-B", anio=2026,
        vig_desde=date(2026, 1, 1), tenant_id=tenant_a.id, activa=True,
    )
    db_session.add(cohorte)

    admin_rol = Rol(nombre="ADMIN_PADRON", descripcion="Admin padron", tenant_id=tenant_a.id)
    db_session.add(admin_rol)
    await db_session.flush()

    perm = Permiso(
        codigo="padron:importar",
        descripcion="Importar padron",
        modulo="padron",
    )
    db_session.add(perm)
    await db_session.flush()

    rp = RolPermiso(
        rol_id=admin_rol.id, permiso_id=perm.id, tenant_id=tenant_a.id,
    )
    db_session.add(rp)

    user = User(
        email="admin_padron@test.com", password_hash=hash_password("pass123!"),
        nombre="Admin", apellidos="Padron", tenant_id=tenant_a.id,
    )
    db_session.add(user)
    await db_session.flush()

    ur = UsuarioRol(
        user_id=user.id, rol_id=admin_rol.id,
        fecha_desde=datetime.now(timezone.utc) - timedelta(days=30),
        tenant_id=tenant_a.id,
    )
    db_session.add(ur)

    viewer_rol = Rol(nombre="VIEWER_PAD", descripcion="Viewer", tenant_id=tenant_a.id)
    db_session.add(viewer_rol)
    await db_session.flush()

    viewer = User(
        email="viewer_pad@test.com", password_hash=hash_password("pass123!"),
        nombre="Viewer", apellidos="Pad", tenant_id=tenant_a.id,
    )
    db_session.add(viewer)
    await db_session.flush()

    viewer_ur = UsuarioRol(
        user_id=viewer.id, rol_id=viewer_rol.id,
        fecha_desde=datetime.now(timezone.utc) - timedelta(days=30),
        tenant_id=tenant_a.id,
    )
    db_session.add(viewer_ur)
    await db_session.commit()

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
                "user_id": user.id,
                "tenant_a_id": tenant_a.id,
                "tenant_b_id": tenant_b.id,
            }


@pytest.mark.needs_db
class TestPadronImport:

    async def test_upload_xlsx_valido_retorna_preview(self, admin_padron_client_and_data):
        data = admin_padron_client_and_data
        xlsx_bytes = _make_xlsx()
        files = {"file": ("alumnos.xlsx", xlsx_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        response = await data["client"].post(
            "/api/padron/import",
            files=files,
            data={"materia_id": data["materia_id"], "cohorte_id": data["cohorte_id"]},
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert "preview_token" in body
        assert body["detected_rows"] == 2
        assert body["filename"] == "alumnos.xlsx"

    async def test_upload_csv_valido_retorna_preview(self, admin_padron_client_and_data):
        data = admin_padron_client_and_data
        files = {"file": ("alumnos.csv", SAMPLE_CSV, "text/csv")}
        response = await data["client"].post(
            "/api/padron/import",
            files=files,
            data={"materia_id": data["materia_id"], "cohorte_id": data["cohorte_id"]},
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert "preview_token" in body
        assert body["detected_rows"] == 2

    async def test_upload_sin_permiso_retorna_403(self, admin_padron_client_and_data):
        data = admin_padron_client_and_data
        files = {"file": ("alumnos.csv", SAMPLE_CSV, "text/csv")}
        response = await data["client"].post(
            "/api/padron/import",
            files=files,
            data={"materia_id": data["materia_id"], "cohorte_id": data["cohorte_id"]},
            headers={"Authorization": f"Bearer {data['viewer_token']}"},
        )
        assert response.status_code == 403

    async def test_confirm_con_token_valido_persiste(self, admin_padron_client_and_data):
        data = admin_padron_client_and_data
        xlsx_bytes = _make_xlsx()
        files = {"file": ("alumnos.xlsx", xlsx_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        preview_resp = await data["client"].post(
            "/api/padron/import",
            files=files,
            data={"materia_id": data["materia_id"], "cohorte_id": data["cohorte_id"]},
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert preview_resp.status_code == 200
        token = preview_resp.json()["preview_token"]

        confirm_resp = await data["client"].post(
            f"/api/padron/confirm/{token}",
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert confirm_resp.status_code == 200, confirm_resp.text
        cbody = confirm_resp.json()
        assert cbody["entries_count"] == 2
        assert "version_id" in cbody

    async def test_confirm_token_invalido_retorna_404(self, admin_padron_client_and_data):
        data = admin_padron_client_and_data
        response = await data["client"].post(
            "/api/padron/confirm/token-invalido",
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert response.status_code == 404

    async def test_confirm_desactiva_version_anterior(self, admin_padron_client_and_data):
        data = admin_padron_client_and_data
        xlsx_bytes = _make_xlsx()
        files = {"file": ("alumnos.xlsx", xlsx_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}

        for _ in range(2):
            preview = await data["client"].post(
                "/api/padron/import",
                files=files,
                data={"materia_id": data["materia_id"], "cohorte_id": data["cohorte_id"]},
                headers={"Authorization": f"Bearer {data['admin_token']}"},
            )
            token = preview.json()["preview_token"]
            await data["client"].post(
                f"/api/padron/confirm/{token}",
                headers={"Authorization": f"Bearer {data['admin_token']}"},
            )

        # Verificar que solo la última versión está activa
        app_ctx = create_app()
        async with LifespanManager(app_ctx):
            transport = ASGITransport(app=app_ctx)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                versions_resp = await client.get(
                    f"/api/padron/versions?materia_id={data['materia_id']}",
                    headers={"Authorization": f"Bearer {data['admin_token']}"},
                )
                assert versions_resp.status_code == 200
                versions = versions_resp.json()
                active = [v for v in versions if v["activa"]]
                assert len(active) == 1

    async def test_import_registra_audit_log(self, admin_padron_client_and_data, db_session, tenant_a):
        data = admin_padron_client_and_data
        xlsx_bytes = _make_xlsx()
        files = {"file": ("alumnos.xlsx", xlsx_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        preview = await data["client"].post(
            "/api/padron/import",
            files=files,
            data={"materia_id": data["materia_id"], "cohorte_id": data["cohorte_id"]},
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        token = preview.json()["preview_token"]
        await data["client"].post(
            f"/api/padron/confirm/{token}",
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )

        stmt = sa.select(AuditLog).where(AuditLog.accion == action_codes.PADRON_CARGAR)
        result = await db_session.execute(stmt)
        logs = result.scalars().all()
        assert len(logs) >= 1

    async def test_vaciar_materia_retorna_200(self, admin_padron_client_and_data):
        data = admin_padron_client_and_data
        response = await data["client"].delete(
            f"/api/padron/vaciar/{data['materia_id']}",
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert "filas_afectadas" in body

    async def test_vaciar_materia_sin_permiso_retorna_403(self, admin_padron_client_and_data):
        data = admin_padron_client_and_data
        response = await data["client"].delete(
            f"/api/padron/vaciar/{data['materia_id']}",
            headers={"Authorization": f"Bearer {data['viewer_token']}"},
        )
        assert response.status_code == 403

    async def test_archivo_vacio_retorna_error(self, admin_padron_client_and_data):
        data = admin_padron_client_and_data
        files = {"file": ("vacio.csv", b"nombre,apellidos\n", "text/csv")}
        response = await data["client"].post(
            "/api/padron/import",
            files=files,
            data={"materia_id": data["materia_id"], "cohorte_id": data["cohorte_id"]},
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert response.status_code == 422

    async def test_columnas_faltantes_retorna_422(self, admin_padron_client_and_data):
        data = admin_padron_client_and_data
        bad_csv = b"nombre,comision\nJuan,A\nMaria,B"
        files = {"file": ("bad.csv", bad_csv, "text/csv")}
        response = await data["client"].post(
            "/api/padron/import",
            files=files,
            data={"materia_id": data["materia_id"], "cohorte_id": data["cohorte_id"]},
            headers={"Authorization": f"Bearer {data['admin_token']}"},
        )
        assert response.status_code == 422
