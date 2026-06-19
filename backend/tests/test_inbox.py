"""Tests para C-20 Inbox: mensajería interna con hilos."""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from jose import jwt

from app.core.config import Settings
from app.core.security import hash_password
from app.main import create_app
from app.models.user import User


@pytest.fixture
async def inbox_users(test_engine, tenant_a, tenant_b, db_session):
    """Three users in tenant_a, one user in tenant_b for cross-tenant tests."""
    settings = Settings()

    u1 = User(
        email="inbox_u1@test.com", password_hash=hash_password("pass123!"),
        nombre="User", apellidos="One", tenant_id=tenant_a.id,
    )
    u2 = User(
        email="inbox_u2@test.com", password_hash=hash_password("pass123!"),
        nombre="User", apellidos="Two", tenant_id=tenant_a.id,
    )
    u3 = User(
        email="inbox_u3@test.com", password_hash=hash_password("pass123!"),
        nombre="User", apellidos="Three", tenant_id=tenant_a.id,
    )
    u4 = User(
        email="inbox_other@test.com", password_hash=hash_password("pass123!"),
        nombre="Other", apellidos="Tenant", tenant_id=tenant_b.id,
    )
    db_session.add_all([u1, u2, u3, u4])
    await db_session.commit()
    for u in [u1, u2, u3, u4]:
        await db_session.refresh(u)

    token_u1 = jwt.encode(
        {"sub": str(u1.id), "tenant_id": str(tenant_a.id),
         "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
        settings.secret_key, algorithm=settings.jwt_algorithm,
    )
    token_u2 = jwt.encode(
        {"sub": str(u2.id), "tenant_id": str(tenant_a.id),
         "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
        settings.secret_key, algorithm=settings.jwt_algorithm,
    )
    token_u3 = jwt.encode(
        {"sub": str(u3.id), "tenant_id": str(tenant_a.id),
         "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
        settings.secret_key, algorithm=settings.jwt_algorithm,
    )
    token_u4 = jwt.encode(
        {"sub": str(u4.id), "tenant_id": str(tenant_b.id),
         "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
        settings.secret_key, algorithm=settings.jwt_algorithm,
    )

    app = create_app()
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield {
                "client": client,
                "token_u1": token_u1,
                "token_u2": token_u2,
                "token_u3": token_u3,
                "token_u4": token_u4,
                "u1": u1, "u2": u2, "u3": u3, "u4": u4,
                "tenant_a_id": tenant_a.id,
                "tenant_b_id": tenant_b.id,
            }


@pytest.mark.needs_db
class TestListThreads:
    """GET /api/inbox — listar hilos donde el usuario es destinatario."""

    async def test_list_threads_vacio(self, inbox_users):
        c = inbox_users["client"]
        token = inbox_users["token_u1"]

        resp = await c.get(
            "/api/inbox",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body == []

    async def test_list_threads_con_mensajes(self, inbox_users):
        c = inbox_users["client"]
        token_u1 = inbox_users["token_u1"]
        token_u2 = inbox_users["token_u2"]
        token_u3 = inbox_users["token_u3"]

        # u2 sends message to u1
        resp = await c.post(
            "/api/inbox",
            json={"destinatario_id": str(inbox_users["u1"].id), "asunto": "Hola", "cuerpo": "Mensaje de prueba"},
            headers={"Authorization": f"Bearer {token_u2}"},
        )
        assert resp.status_code == 201

        # u3 sends message to u1
        resp = await c.post(
            "/api/inbox",
            json={"destinatario_id": str(inbox_users["u1"].id), "asunto": "Otro", "cuerpo": "Segundo mensaje"},
            headers={"Authorization": f"Bearer {token_u3}"},
        )
        assert resp.status_code == 201

        # u1 lists inbox
        resp = await c.get(
            "/api/inbox",
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 2
        asuntos = {m["asunto"] for m in body}
        assert "Hola" in asuntos
        assert "Otro" in asuntos

    async def test_list_threads_sin_auth(self, async_client):
        resp = await async_client.get("/api/inbox")
        assert resp.status_code in (401, 403)


@pytest.mark.needs_db
class TestGetThread:
    """GET /api/inbox/{id} — leer un hilo completo."""

    async def test_get_thread_como_destinatario(self, inbox_users):
        c = inbox_users["client"]
        token_u1 = inbox_users["token_u1"]
        token_u2 = inbox_users["token_u2"]
        u1 = inbox_users["u1"]

        # u2 sends to u1
        resp = await c.post(
            "/api/inbox",
            json={"destinatario_id": str(u1.id), "asunto": "Consulta", "cuerpo": "Necesito info"},
            headers={"Authorization": f"Bearer {token_u2}"},
        )
        assert resp.status_code == 201
        msg_id = resp.json()["id"]

        # u1 reads the thread
        resp = await c.get(
            f"/api/inbox/{msg_id}",
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["mensaje_raiz"]["id"] == msg_id
        assert body["mensaje_raiz"]["asunto"] == "Consulta"
        assert body["mensaje_raiz"]["leido"] is True  # Se marca como leído
        assert body["respuestas"] == []

    async def test_get_thread_como_participante(self, inbox_users):
        c = inbox_users["client"]
        token_u1 = inbox_users["token_u1"]
        token_u2 = inbox_users["token_u2"]
        token_u3 = inbox_users["token_u3"]
        u1 = inbox_users["u1"]

        # u2 sends to u1
        resp = await c.post(
            "/api/inbox",
            json={"destinatario_id": str(u1.id), "asunto": "Tema", "cuerpo": "Inicio del hilo"},
            headers={"Authorization": f"Bearer {token_u2}"},
        )
        msg_id = resp.json()["id"]

        # u1 replies to the thread (u1 is destinatario, can reply)
        resp = await c.post(
            f"/api/inbox/{msg_id}/reply",
            json={"cuerpo": "Respuesta de u1"},
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert resp.status_code == 201

        # u2 replies to own thread (u2 is remitente, can reply)
        resp = await c.post(
            f"/api/inbox/{msg_id}/reply",
            json={"cuerpo": "Respuesta de u2"},
            headers={"Authorization": f"Bearer {token_u2}"},
        )
        assert resp.status_code == 201

        # u1 can read the thread
        resp = await c.get(
            f"/api/inbox/{msg_id}",
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["respuestas"]) == 2

        # u2 (remitente original) can also read
        resp = await c.get(
            f"/api/inbox/{msg_id}",
            headers={"Authorization": f"Bearer {token_u2}"},
        )
        assert resp.status_code == 200

        # u3 is NOT a participant, should get 404
        resp = await c.post(
            f"/api/inbox/{msg_id}/reply",
            json={"cuerpo": "No debería poder"},
            headers={"Authorization": f"Bearer {token_u3}"},
        )
        assert resp.status_code == 404

    async def test_get_thread_sin_permiso(self, inbox_users):
        c = inbox_users["client"]
        token_u2 = inbox_users["token_u2"]
        token_u3 = inbox_users["token_u3"]
        u1 = inbox_users["u1"]

        # u2 sends to u1
        resp = await c.post(
            "/api/inbox",
            json={"destinatario_id": str(u1.id), "asunto": "Privado", "cuerpo": "Solo para u1"},
            headers={"Authorization": f"Bearer {token_u2}"},
        )
        msg_id = resp.json()["id"]

        # u3 tries to read — should get 404
        resp = await c.get(
            f"/api/inbox/{msg_id}",
            headers={"Authorization": f"Bearer {token_u3}"},
        )
        assert resp.status_code == 404

    async def test_get_thread_inexistente(self, inbox_users):
        c = inbox_users["client"]
        token_u1 = inbox_users["token_u1"]

        fake_id = uuid.uuid4()
        resp = await c.get(
            f"/api/inbox/{fake_id}",
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert resp.status_code == 404


@pytest.mark.needs_db
class TestCreateMessage:
    """POST /api/inbox — crear un nuevo mensaje (inicia un hilo)."""

    async def test_create_message_ok(self, inbox_users):
        c = inbox_users["client"]
        token_u1 = inbox_users["token_u1"]
        u2 = inbox_users["u2"]

        resp = await c.post(
            "/api/inbox",
            json={"destinatario_id": str(u2.id), "asunto": "Saludo", "cuerpo": "Hola, cómo estás?"},
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["asunto"] == "Saludo"
        assert body["cuerpo"] == "Hola, cómo estás?"
        assert body["remitente"]["id"] == str(inbox_users["u1"].id)
        assert body["destinatario"]["id"] == str(u2.id)
        assert body["mensaje_padre_id"] is None
        assert body["leido"] is False

    async def test_create_message_destinatario_inexistente(self, inbox_users):
        c = inbox_users["client"]
        token_u1 = inbox_users["token_u1"]

        fake_id = uuid.uuid4()
        resp = await c.post(
            "/api/inbox",
            json={"destinatario_id": str(fake_id), "asunto": "Test", "cuerpo": "Body"},
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert resp.status_code == 404

    async def test_create_message_sin_asunto(self, inbox_users):
        c = inbox_users["client"]
        token_u1 = inbox_users["token_u1"]
        u2 = inbox_users["u2"]

        resp = await c.post(
            "/api/inbox",
            json={"destinatario_id": str(u2.id), "asunto": "", "cuerpo": "Body"},
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert resp.status_code == 422

    async def test_create_message_sin_cuerpo(self, inbox_users):
        c = inbox_users["client"]
        token_u1 = inbox_users["token_u1"]
        u2 = inbox_users["u2"]

        resp = await c.post(
            "/api/inbox",
            json={"destinatario_id": str(u2.id), "asunto": "Test", "cuerpo": ""},
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert resp.status_code == 422

    async def test_create_message_sin_auth(self, async_client):
        resp = await async_client.post(
            "/api/inbox",
            json={"destinatario_id": str(uuid.uuid4()), "asunto": "X", "cuerpo": "Y"},
        )
        assert resp.status_code in (401, 403)


@pytest.mark.needs_db
class TestReplyToThread:
    """POST /api/inbox/{id}/reply — responder a un hilo existente."""

    async def test_reply_to_thread_ok(self, inbox_users):
        c = inbox_users["client"]
        token_u1 = inbox_users["token_u1"]
        token_u2 = inbox_users["token_u2"]
        u1 = inbox_users["u1"]
        u2 = inbox_users["u2"]

        # u2 sends to u1
        resp = await c.post(
            "/api/inbox",
            json={"destinatario_id": str(u1.id), "asunto": "Pregunta", "cuerpo": "¿Tenés el archivo?"},
            headers={"Authorization": f"Bearer {token_u2}"},
        )
        msg_id = resp.json()["id"]

        # u1 replies
        resp = await c.post(
            f"/api/inbox/{msg_id}/reply",
            json={"cuerpo": "Sí, acá está"},
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["cuerpo"] == "Sí, acá está"
        assert body["remitente"]["id"] == str(u1.id)
        assert body["destinatario"]["id"] == str(u2.id)
        assert body["mensaje_padre_id"] == msg_id

    async def test_reply_sin_participante(self, inbox_users):
        c = inbox_users["client"]
        token_u2 = inbox_users["token_u2"]
        token_u3 = inbox_users["token_u3"]
        u1 = inbox_users["u1"]

        # u2 sends to u1
        resp = await c.post(
            "/api/inbox",
            json={"destinatario_id": str(u1.id), "asunto": "Exclusivo", "cuerpo": "Solo u1 y u2"},
            headers={"Authorization": f"Bearer {token_u2}"},
        )
        msg_id = resp.json()["id"]

        # u3 tries to reply — should get 404
        resp = await c.post(
            f"/api/inbox/{msg_id}/reply",
            json={"cuerpo": "Quiero participar"},
            headers={"Authorization": f"Bearer {token_u3}"},
        )
        assert resp.status_code == 404

    async def test_reply_sin_cuerpo(self, inbox_users):
        c = inbox_users["client"]
        token_u1 = inbox_users["token_u1"]
        token_u2 = inbox_users["token_u2"]
        u1 = inbox_users["u1"]

        # u2 sends to u1
        resp = await c.post(
            "/api/inbox",
            json={"destinatario_id": str(u1.id), "asunto": "Tema", "cuerpo": "Cuerpo"},
            headers={"Authorization": f"Bearer {token_u2}"},
        )
        msg_id = resp.json()["id"]

        # u1 replies with empty body
        resp = await c.post(
            f"/api/inbox/{msg_id}/reply",
            json={"cuerpo": ""},
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert resp.status_code == 422

    async def test_reply_a_hilo_inexistente(self, inbox_users):
        c = inbox_users["client"]
        token_u1 = inbox_users["token_u1"]

        fake_id = uuid.uuid4()
        resp = await c.post(
            f"/api/inbox/{fake_id}/reply",
            json={"cuerpo": "Respuesta"},
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert resp.status_code == 404


@pytest.mark.needs_db
class TestTenantIsolation:
    """Aislamiento de tenant en mensajería."""

    async def test_tenant_isolation_inbox(self, inbox_users):
        c = inbox_users["client"]
        token_u1 = inbox_users["token_u1"]
        token_u4 = inbox_users["token_u4"]
        u2 = inbox_users["u2"]

        # u1 sends to u2 in tenant_a
        resp = await c.post(
            "/api/inbox",
            json={"destinatario_id": str(u2.id), "asunto": "Tenant A", "cuerpo": "Mensaje en tenant A"},
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert resp.status_code == 201
        msg_id_a = resp.json()["id"]

        # u4 from tenant_b tries to access the message from tenant_a
        resp = await c.get(
            f"/api/inbox/{msg_id_a}",
            headers={"Authorization": f"Bearer {token_u4}"},
        )
        assert resp.status_code == 404

    async def test_cant_send_to_user_in_other_tenant(self, inbox_users):
        c = inbox_users["client"]
        token_u1 = inbox_users["token_u1"]
        u4 = inbox_users["u4"]  # tenant_b

        # u1 (tenant_a) tries to send to u4 (tenant_b)
        resp = await c.post(
            "/api/inbox",
            json={"destinatario_id": str(u4.id), "asunto": "Cross-tenant", "cuerpo": "Should fail"},
            headers={"Authorization": f"Bearer {token_u1}"},
        )
        assert resp.status_code == 404
