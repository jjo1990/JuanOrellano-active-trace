"""Tests para TareaService (C-16) — F8.1, F8.2, F8.3."""

import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tarea import Tarea
from app.models.user import User
from app.schemas.tarea import (
    ComentarioCreateRequest,
    TareaCreateRequest,
    TareaDelegarRequest,
    TareaEstadoRequest,
    TareaUpdateRequest,
)
from app.services.tarea_service import TareaService


@pytest.fixture
async def seed_tarea_service(tenant_a, db_session: AsyncSession):
    tenant_id = tenant_a.id

    coordinador = User(
        email="coord_tarea@test.com", password_hash="hash",
        nombre="Coord", apellidos="Tarea", tenant_id=tenant_id,
    )
    profesor = User(
        email="profe_tarea@test.com", password_hash="hash",
        nombre="Profe", apellidos="Tarea", tenant_id=tenant_id,
    )
    otro_profesor = User(
        email="otro_tarea@test.com", password_hash="hash",
        nombre="Otro", apellidos="Profesor", tenant_id=tenant_id,
    )
    db_session.add_all([coordinador, profesor, otro_profesor])
    await db_session.commit()
    for u in [coordinador, profesor, otro_profesor]:
        await db_session.refresh(u)

    return {
        "tenant_id": tenant_id,
        "coordinador_id": coordinador.id,
        "profesor_id": profesor.id,
        "otro_profesor_id": otro_profesor.id,
    }


@pytest.mark.needs_db
class TestTareaServiceCrear:
    async def test_create_tarea_basica(self, seed_tarea_service, db_session):
        svc = TareaService(db_session, seed_tarea_service["tenant_id"])
        data = TareaCreateRequest(
            asignado_a=seed_tarea_service["profesor_id"],
            descripcion="Revisar entregas del parcial",
        )
        tarea = await svc.crear_tarea(
            data, seed_tarea_service["tenant_id"], seed_tarea_service["coordinador_id"],
        )
        assert tarea.id is not None
        assert tarea.estado == "Pendiente"
        assert tarea.asignado_a == seed_tarea_service["profesor_id"]
        assert tarea.asignado_por == seed_tarea_service["coordinador_id"]


@pytest.mark.needs_db
class TestTareaServiceMisTareas:
    async def test_list_mis_tareas(self, seed_tarea_service, db_session):
        svc = TareaService(db_session, seed_tarea_service["tenant_id"])
        t_id = seed_tarea_service["tenant_id"]

        await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["profesor_id"],
                descripcion="Tarea 1",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )
        await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["profesor_id"],
                descripcion="Tarea 2",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )
        await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["otro_profesor_id"],
                descripcion="Tarea de otro",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )

        resultados = await svc.list_mis_tareas(
            t_id, seed_tarea_service["profesor_id"],
        )
        assert len(resultados) == 2
        descs = {r.descripcion for r in resultados}
        assert "Tarea 1" in descs
        assert "Tarea 2" in descs

    async def test_list_mis_tareas_filter_estado(self, seed_tarea_service, db_session):
        svc = TareaService(db_session, seed_tarea_service["tenant_id"])
        t_id = seed_tarea_service["tenant_id"]

        created = await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["profesor_id"],
                descripcion="Revisar planillas",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )

        await svc.cambiar_estado(
            created.id,
            TareaEstadoRequest(estado="En progreso"),
            t_id, seed_tarea_service["profesor_id"],
        )

        resultados = await svc.list_mis_tareas(
            t_id, seed_tarea_service["profesor_id"], estado="Pendiente",
        )
        assert len(resultados) == 0

        resultados = await svc.list_mis_tareas(
            t_id, seed_tarea_service["profesor_id"], estado="En progreso",
        )
        assert len(resultados) == 1


@pytest.mark.needs_db
class TestTareaServiceEstado:
    async def test_asignado_cambia_a_en_progreso(self, seed_tarea_service, db_session):
        svc = TareaService(db_session, seed_tarea_service["tenant_id"])
        t_id = seed_tarea_service["tenant_id"]

        tarea = await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["profesor_id"],
                descripcion="Test estado",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )

        actualizada = await svc.cambiar_estado(
            tarea.id,
            TareaEstadoRequest(estado="En progreso"),
            t_id, seed_tarea_service["profesor_id"],
        )
        assert actualizada.estado == "En progreso"

    async def test_no_asignado_sin_permiso_da_403(self, seed_tarea_service, db_session):
        svc = TareaService(db_session, seed_tarea_service["tenant_id"])
        t_id = seed_tarea_service["tenant_id"]

        tarea = await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["profesor_id"],
                descripcion="Test permisos",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )

        with pytest.raises(HTTPException) as exc_info:
            await svc.cambiar_estado(
                tarea.id,
                TareaEstadoRequest(estado="En progreso"),
                t_id, seed_tarea_service["otro_profesor_id"],
            )
        assert exc_info.value.status_code == 403

    async def test_asignado_puede_resolver(self, seed_tarea_service, db_session):
        svc = TareaService(db_session, seed_tarea_service["tenant_id"])
        t_id = seed_tarea_service["tenant_id"]

        tarea = await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["profesor_id"],
                descripcion="Resolver",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )

        actualizada = await svc.cambiar_estado(
            tarea.id,
            TareaEstadoRequest(estado="Resuelta"),
            t_id, seed_tarea_service["profesor_id"],
        )
        assert actualizada.estado == "Resuelta"

    async def test_cancelar_desde_cualquier_estado(self, seed_tarea_service, db_session):
        svc = TareaService(db_session, seed_tarea_service["tenant_id"])
        t_id = seed_tarea_service["tenant_id"]

        tarea = await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["profesor_id"],
                descripcion="Cancelar test",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )

        actualizada = await svc.cambiar_estado(
            tarea.id,
            TareaEstadoRequest(estado="Cancelada"),
            t_id, seed_tarea_service["profesor_id"],
        )
        assert actualizada.estado == "Cancelada"

    async def test_estado_invalido_rechaza(self, seed_tarea_service, db_session):
        svc = TareaService(db_session, seed_tarea_service["tenant_id"])
        t_id = seed_tarea_service["tenant_id"]

        tarea = await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["profesor_id"],
                descripcion="Estado invalido",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )

        with pytest.raises(HTTPException) as exc_info:
            await svc.cambiar_estado(
                tarea.id,
                TareaEstadoRequest(estado="Inexistente"),
                t_id, seed_tarea_service["profesor_id"],
            )
        assert exc_info.value.status_code == 422


@pytest.mark.needs_db
class TestTareaServiceDelegar:
    async def test_asignado_delega_a_otro(self, seed_tarea_service, db_session):
        svc = TareaService(db_session, seed_tarea_service["tenant_id"])
        t_id = seed_tarea_service["tenant_id"]

        tarea = await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["profesor_id"],
                descripcion="Delegar esta",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )

        delegada = await svc.delegar_tarea(
            tarea.id,
            TareaDelegarRequest(nuevo_asignado_id=seed_tarea_service["otro_profesor_id"]),
            t_id, seed_tarea_service["profesor_id"],
        )
        assert delegada.asignado_a == seed_tarea_service["otro_profesor_id"]
        assert delegada.asignado_por == seed_tarea_service["coordinador_id"]

        comentarios = await svc.list_comentarios(t_id, tarea.id)
        assert len(comentarios) == 1
        assert "delegada" in comentarios[0].texto.lower()

    async def test_no_asignado_no_puede_delegar(self, seed_tarea_service, db_session):
        svc = TareaService(db_session, seed_tarea_service["tenant_id"])
        t_id = seed_tarea_service["tenant_id"]

        tarea = await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["profesor_id"],
                descripcion="No delegable por otro",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )

        with pytest.raises(HTTPException) as exc_info:
            await svc.delegar_tarea(
                tarea.id,
                TareaDelegarRequest(nuevo_asignado_id=seed_tarea_service["otro_profesor_id"]),
                t_id, seed_tarea_service["otro_profesor_id"],
            )
        assert exc_info.value.status_code == 403


@pytest.mark.needs_db
class TestTareaServiceAdmin:
    async def test_admin_list_with_filters(self, seed_tarea_service, db_session):
        svc = TareaService(db_session, seed_tarea_service["tenant_id"])
        t_id = seed_tarea_service["tenant_id"]

        await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["profesor_id"],
                descripcion="Admin tarea 1",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )
        await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["otro_profesor_id"],
                descripcion="Admin tarea 2",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )

        todas = await svc.list_admin(t_id)
        assert len(todas) == 2

        filtradas = await svc.list_admin(
            t_id, asignado_a=seed_tarea_service["profesor_id"],
        )
        assert len(filtradas) == 1
        assert filtradas[0].descripcion == "Admin tarea 1"

    async def test_admin_search_q(self, seed_tarea_service, db_session):
        svc = TareaService(db_session, seed_tarea_service["tenant_id"])
        t_id = seed_tarea_service["tenant_id"]

        await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["profesor_id"],
                descripcion="Buscar parciales",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )
        await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["otro_profesor_id"],
                descripcion="Revisar finales",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )

        resultados = await svc.list_admin(t_id, q="parcial")
        assert len(resultados) == 1
        assert resultados[0].descripcion == "Buscar parciales"


@pytest.mark.needs_db
class TestTareaServiceComentarios:
    async def test_add_comment(self, seed_tarea_service, db_session):
        svc = TareaService(db_session, seed_tarea_service["tenant_id"])
        t_id = seed_tarea_service["tenant_id"]

        tarea = await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["profesor_id"],
                descripcion="Con comentarios",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )

        comentario = await svc.agregar_comentario(
            tarea.id,
            ComentarioCreateRequest(texto="Adjunto evidencia"),
            t_id, seed_tarea_service["profesor_id"],
        )
        assert comentario.id is not None
        assert comentario.texto == "Adjunto evidencia"
        assert comentario.autor_id == seed_tarea_service["profesor_id"]

    async def test_list_comments(self, seed_tarea_service, db_session):
        svc = TareaService(db_session, seed_tarea_service["tenant_id"])
        t_id = seed_tarea_service["tenant_id"]

        tarea = await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["profesor_id"],
                descripcion="Multiples comentarios",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )

        await svc.agregar_comentario(
            tarea.id,
            ComentarioCreateRequest(texto="Primero"),
            t_id, seed_tarea_service["profesor_id"],
        )
        await svc.agregar_comentario(
            tarea.id,
            ComentarioCreateRequest(texto="Segundo"),
            t_id, seed_tarea_service["coordinador_id"],
        )

        comentarios = await svc.list_comentarios(t_id, tarea.id)
        assert len(comentarios) == 2
        assert comentarios[0].texto == "Primero"
        assert comentarios[1].texto == "Segundo"

    async def test_empty_comments(self, seed_tarea_service, db_session):
        svc = TareaService(db_session, seed_tarea_service["tenant_id"])
        t_id = seed_tarea_service["tenant_id"]

        tarea = await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["profesor_id"],
                descripcion="Sin comentarios",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )

        comentarios = await svc.list_comentarios(t_id, tarea.id)
        assert len(comentarios) == 0


@pytest.mark.needs_db
class TestTareaServiceEditar:
    async def test_edit_descripcion(self, seed_tarea_service, db_session):
        svc = TareaService(db_session, seed_tarea_service["tenant_id"])
        t_id = seed_tarea_service["tenant_id"]

        tarea = await svc.crear_tarea(
            TareaCreateRequest(
                asignado_a=seed_tarea_service["profesor_id"],
                descripcion="Original",
            ),
            t_id, seed_tarea_service["coordinador_id"],
        )

        actualizada = await svc.editar_tarea(
            tarea.id,
            TareaUpdateRequest(descripcion="Editada"),
            t_id,
        )
        assert actualizada.descripcion == "Editada"
