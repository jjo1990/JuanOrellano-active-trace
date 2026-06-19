import html
import logging
import uuid
from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.instancia_encuentro import InstanciaEncuentro
from app.models.slot_encuentro import SlotEncuentro
from app.repositories.instancia_encuentro_repository import InstanciaEncuentroRepository
from app.repositories.slot_encuentro_repository import SlotEncuentroRepository
from app.schemas.encuentro import (
    AdminEncuentrosFilterParams,
    InstanciaCreateRequest,
    InstanciaResponse,
    InstanciaUpdateRequest,
    SlotCreateRequest,
    SlotResponse,
)

logger = logging.getLogger(__name__)

DIAS_SEMANA = {
    "Lunes": 0, "Martes": 1, "Miercoles": 2, "Jueves": 3,
    "Viernes": 4, "Sabado": 5, "Domingo": 6,
}


class EncuentroService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id
        self._slot_repo = SlotEncuentroRepository(session, tenant_id)
        self._inst_repo = InstanciaEncuentroRepository(session, tenant_id)

    async def crear_slot(
        self, data: SlotCreateRequest, tenant_id: uuid.UUID, user_id: uuid.UUID,
    ) -> SlotEncuentro:
        slot = SlotEncuentro(
            titulo=data.titulo,
            hora=data.hora,
            dia_semana=data.dia_semana,
            fecha_inicio=data.fecha_inicio,
            cant_semanas=data.cant_semanas,
            fecha_unica=data.fecha_unica,
            meet_url=data.meet_url,
            materia_id=data.materia_id,
            asignacion_id=data.asignacion_id,
        )
        slot = await self._slot_repo.create(slot)
        await self._generar_instancias(
            slot, data.cant_semanas, data.fecha_inicio, data.fecha_unica, data.dia_semana, data.hora, data.titulo,
        )
        return slot

    async def _generar_instancias(
        self, slot: SlotEncuentro, cant_semanas: int,
        fecha_inicio: date | None, fecha_unica: date | None,
        dia_semana: str | None, hora, titulo: str,
    ) -> None:
        if fecha_unica is not None:
            inst = InstanciaEncuentro(
                slot_id=slot.id,
                materia_id=slot.materia_id,
                fecha=fecha_unica,
                hora=hora,
                titulo=titulo,
                estado="Programado",
                tenant_id=self._tenant_id,
            )
            self._session.add(inst)
            await self._session.flush()
            return

        if cant_semanas > 0 and fecha_inicio is not None and dia_semana is not None:
            target_weekday = DIAS_SEMANA.get(dia_semana, 0)
            current = fecha_inicio
            for _ in range(cant_semanas):
                days_offset = (target_weekday - current.weekday()) % 7
                real_date = current + timedelta(days=days_offset)
                inst = InstanciaEncuentro(
                    slot_id=slot.id,
                    materia_id=slot.materia_id,
                    fecha=real_date,
                    hora=hora,
                    titulo=titulo,
                    estado="Programado",
                    meet_url=slot.meet_url,
                    tenant_id=self._tenant_id,
                )
                self._session.add(inst)
                current = real_date + timedelta(days=7)
            await self._session.flush()

    async def crear_instancia(
        self, data: InstanciaCreateRequest, tenant_id: uuid.UUID, user_id: uuid.UUID,
    ) -> InstanciaEncuentro:
        inst = InstanciaEncuentro(
            slot_id=None,
            materia_id=data.materia_id,
            fecha=data.fecha,
            hora=data.hora,
            titulo=data.titulo,
            estado="Programado",
            meet_url=data.meet_url,
            tenant_id=self._tenant_id,
        )
        self._session.add(inst)
        await self._session.flush()
        await self._session.refresh(inst)
        return inst

    async def editar_instancia(
        self, instancia_id: uuid.UUID, data: InstanciaUpdateRequest,
        tenant_id: uuid.UUID, user_id: uuid.UUID,
    ) -> InstanciaEncuentro:
        inst = await self._inst_repo.get(instancia_id)
        if inst is None:
            raise HTTPException(status_code=404, detail="Instancia no encontrada.")
        if data.estado is not None:
            inst.estado = data.estado
        if data.meet_url is not None:
            inst.meet_url = data.meet_url
        if data.video_url is not None:
            inst.video_url = data.video_url
        if data.comentario is not None:
            inst.comentario = data.comentario
        await self._session.flush()
        return inst

    async def get_slot_con_instancias(
        self, slot_id: uuid.UUID, tenant_id: uuid.UUID,
    ) -> SlotEncuentro:
        slot = await self._slot_repo.get_by_id(slot_id, tenant_id)
        if slot is None:
            raise HTTPException(status_code=404, detail="Slot no encontrado.")
        return slot

    async def generar_html_aula_virtual(
        self, slot_id: uuid.UUID, tenant_id: uuid.UUID,
    ) -> str:
        slot = await self._slot_repo.get_by_id(slot_id, tenant_id)
        if slot is None:
            raise HTTPException(status_code=404, detail="Slot no encontrado.")
        instancias = await self._inst_repo.list_by_slot(slot_id, tenant_id)

        if not instancias:
            return "<p>No hay encuentros programados para este slot.</p>"

        rows = ""
        for inst in instancias:
            meet_link = f'<a href="{html.escape(inst.meet_url)}" target="_blank">Unirse</a>' if inst.meet_url else "—"
            video_link = f'<a href="{html.escape(inst.video_url)}" target="_blank">Ver grabación</a>' if inst.video_url else "—"
            rows += (
                f"<tr>"
                f"<td>{html.escape(str(inst.fecha))}</td>"
                f"<td>{html.escape(str(inst.hora))}</td>"
                f"<td>{html.escape(inst.estado)}</td>"
                f"<td>{meet_link}</td>"
                f"<td>{video_link}</td>"
                f"</tr>"
            )

        return (
            f'<div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">'
            f'<h2>{html.escape(slot.titulo)}</h2>'
            f'<table style="width:100%; border-collapse:collapse;">'
            f'<thead><tr>'
            f'<th style="text-align:left; padding:8px; border-bottom:2px solid #ddd;">Fecha</th>'
            f'<th style="text-align:left; padding:8px; border-bottom:2px solid #ddd;">Horario</th>'
            f'<th style="text-align:left; padding:8px; border-bottom:2px solid #ddd;">Estado</th>'
            f'<th style="text-align:left; padding:8px; border-bottom:2px solid #ddd;">Videoconferencia</th>'
            f'<th style="text-align:left; padding:8px; border-bottom:2px solid #ddd;">Grabación</th>'
            f'</tr></thead>'
            f'<tbody>{rows}</tbody>'
            f'</table></div>'
        )

    async def list_mis_encuentros(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID,
    ) -> list[SlotResponse]:
        from sqlalchemy import select
        from app.models.asignacion import Asignacion

        stmt = (
            select(Asignacion.materia_id)
            .where(
                Asignacion.usuario_id == user_id,
                Asignacion.tenant_id == tenant_id,
                Asignacion.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        materia_ids = [row[0] for row in result.fetchall()]

        if not materia_ids:
            return []

        slots = []
        for mid in materia_ids:
            by_mat = await self._slot_repo.list_by_materia(mid, tenant_id)
            slots.extend(by_mat)

        response = []
        for slot in slots:
            instancias = await self._inst_repo.list_by_slot(slot.id, tenant_id)
            sr = SlotResponse(
                id=slot.id,
                titulo=slot.titulo,
                hora=slot.hora,
                dia_semana=slot.dia_semana,
                fecha_inicio=slot.fecha_inicio,
                cant_semanas=slot.cant_semanas,
                fecha_unica=slot.fecha_unica,
                meet_url=slot.meet_url,
                materia_id=slot.materia_id,
                asignacion_id=slot.asignacion_id,
                created_at=slot.created_at,
                instancias=[
                    InstanciaResponse.model_validate(i) for i in instancias
                ],
            )
            response.append(sr)
        return response

    async def list_admin(
        self, tenant_id: uuid.UUID, filtros: AdminEncuentrosFilterParams,
    ) -> list[SlotResponse]:
        slots = await self._slot_repo.list()
        if filtros.materia_id is not None:
            slots = [s for s in slots if s.materia_id == filtros.materia_id]

        response = []
        for slot in slots:
            instancias = await self._inst_repo.list_by_slot(slot.id, tenant_id)
            if filtros.estado is not None:
                instancias = [i for i in instancias if i.estado == filtros.estado]
            if filtros.fecha_desde is not None:
                instancias = [i for i in instancias if i.fecha >= filtros.fecha_desde]
            if filtros.fecha_hasta is not None:
                instancias = [i for i in instancias if i.fecha <= filtros.fecha_hasta]

            if not instancias and (filtros.estado or filtros.fecha_desde or filtros.fecha_hasta):
                continue

            sr = SlotResponse(
                id=slot.id,
                titulo=slot.titulo,
                hora=slot.hora,
                dia_semana=slot.dia_semana,
                fecha_inicio=slot.fecha_inicio,
                cant_semanas=slot.cant_semanas,
                fecha_unica=slot.fecha_unica,
                meet_url=slot.meet_url,
                materia_id=slot.materia_id,
                asignacion_id=slot.asignacion_id,
                created_at=slot.created_at,
                instancias=[
                    InstanciaResponse.model_validate(i) for i in instancias
                ],
            )
            response.append(sr)
        return response
