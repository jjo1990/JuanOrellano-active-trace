from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timezone

from sqlalchemy import select as sa_select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.action_codes import COMUNICACION_ENVIAR
from app.models.audit_log import AuditLog
from app.models.calificacion import Calificacion
from app.models.comunicacion import Comunicacion
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.repositories.audit_log import AuditLogRepository
from app.repositories.calificaciones_repository import CalificacionesRepository
from app.repositories.comunicacion_repository import ComunicacionRepository
from app.repositories.padron_repository import PadronRepository
from app.schemas.comunicacion import (
    CancelarRequest,
    ComunicacionDTO,
    EnviarRequest,
    EnviarResponse,
    LoteStatusResponse,
    PreviewItemDTO,
    PreviewRequest,
    PreviewResponse,
)

logger = logging.getLogger(__name__)

VALID_TRANSITIONS = {
    ("Pendiente", "Enviando"),
    ("Pendiente", "Cancelado"),
    ("Enviando", "Enviado"),
    ("Enviando", "Error"),
}


def validate_transition(estado_actual: str, estado_nuevo: str) -> None:
    if (estado_actual, estado_nuevo) not in VALID_TRANSITIONS:
        validas = [t[1] for t in VALID_TRANSITIONS if t[0] == estado_actual]
        raise ValueError(
            f"Transición inválida: '{estado_actual}' → '{estado_nuevo}'. "
            f"Transiciones válidas desde '{estado_actual}': {validas}"
        )


def render_template(template: str, context: dict[str, str]) -> str:
    return re.sub(
        r"\{\{(\w+)\}\}",
        lambda m: context.get(m.group(1), m.group(0)),
        template,
    )


def _comunicacion_to_dto(com: Comunicacion) -> ComunicacionDTO:
    return ComunicacionDTO(
        id=com.id,
        enviado_por=com.enviado_por,
        materia_id=com.materia_id,
        destinatario=com.destinatario or "",
        asunto=com.asunto,
        cuerpo=com.cuerpo,
        estado=com.estado,
        lote_id=com.lote_id,
        enviado_at=com.enviado_at,
        created_at=com.created_at,
    )


class ComunicacionService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id
        self._com_repo = ComunicacionRepository(session, tenant_id)
        self._padron_repo = PadronRepository(session, tenant_id)
        self._cal_repo = CalificacionesRepository(session, tenant_id)
        self._audit_repo = AuditLogRepository(session)

    async def _get_materia_nombre(self, materia_id: uuid.UUID) -> str:
        stmt = sa_select(Materia.nombre).where(
            Materia.id == materia_id,
            Materia.tenant_id == self._tenant_id,
            Materia.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        nombre = result.scalar_one_or_none()
        return nombre or ""

    async def _get_entrada(self, entrada_id: uuid.UUID) -> EntradaPadron | None:
        return await self._padron_repo._entrada_repo.get(entrada_id)

    async def _get_calificaciones_por_entrada(
        self, entrada_id: uuid.UUID,
    ) -> list[Calificacion]:
        return list(await self._cal_repo.get_calificaciones_by_entrada(entrada_id))

    async def _build_context(
        self, entrada: EntradaPadron, materia_nombre: str,
    ) -> dict[str, str]:
        calificaciones = await self._get_calificaciones_por_entrada(entrada.id)
        notas_numericas = [c.nota_numerica for c in calificaciones if c.nota_numerica is not None]

        context: dict[str, str] = {
            "nombre": f"{entrada.nombre} {entrada.apellidos}".strip(),
            "materia": materia_nombre,
            "link_materia": "",
        }

        if notas_numericas:
            context["nota_promedio"] = str(round(sum(notas_numericas) / len(notas_numericas), 2))

        return context

    async def preview(self, request: PreviewRequest) -> PreviewResponse:
        materia_nombre = await self._get_materia_nombre(request.materia_id)
        previews: list[PreviewItemDTO] = []

        for alumno_id in request.alumno_ids:
            entrada = await self._get_entrada(alumno_id)
            if entrada is None:
                previews.append(PreviewItemDTO(
                    alumno_id=alumno_id,
                    nombre="",
                    asunto=request.template,
                    cuerpo=request.template,
                ))
                continue

            context = await self._build_context(entrada, materia_nombre)
            cuerpo = render_template(request.template, context)
            asunto = render_template(request.template, context)

            previews.append(PreviewItemDTO(
                alumno_id=alumno_id,
                nombre=f"{entrada.nombre} {entrada.apellidos}".strip(),
                asunto=asunto,
                cuerpo=cuerpo,
            ))

        return PreviewResponse(previews=previews)

    async def enviar(
        self, request: EnviarRequest, user_id: uuid.UUID,
    ) -> EnviarResponse:
        lote_id = uuid.uuid4()
        materia_nombre = await self._get_materia_nombre(request.materia_id)
        count = 0

        for alumno_id in request.alumno_ids:
            entrada = await self._get_entrada(alumno_id)
            if entrada is None:
                continue

            context = await self._build_context(entrada, materia_nombre)
            cuerpo = render_template(request.template, context)
            asunto = render_template(request.asunto, context)
            destinatario = entrada.email or ""

            com = Comunicacion(
                tenant_id=self._tenant_id,
                enviado_por=user_id,
                materia_id=request.materia_id,
                destinatario=destinatario,
                asunto=asunto,
                cuerpo=cuerpo,
                estado="Pendiente",
                lote_id=lote_id,
                lote_aprobado=False,
            )
            await self._com_repo.create(com)
            count += 1

            await self._auditar(
                actor_id=user_id,
                accion=COMUNICACION_ENVIAR,
                detalle={
                    "comunicacion_id": str(com.id),
                    "lote_id": str(lote_id),
                    "materia_id": str(request.materia_id),
                    "alumno_id": str(alumno_id),
                },
            )

        await self._session.commit()

        return EnviarResponse(
            lote_id=lote_id,
            count=count,
            estado="Pendiente",
        )

    async def aprobar_lote(
        self, lote_id: uuid.UUID, user_id: uuid.UUID,
    ) -> LoteStatusResponse:
        count = await self._com_repo.aprobar_lote(lote_id)
        await self._auditar(
            actor_id=user_id,
            accion=COMUNICACION_ENVIAR,
            detalle={
                "accion": "aprobar_lote",
                "lote_id": str(lote_id),
                "afectadas": count,
            },
        )
        await self._session.commit()
        return await self.get_lote_status(lote_id)

    async def cancelar_lote(
        self, lote_id: uuid.UUID, user_id: uuid.UUID, motivo: str | None = None,
    ) -> LoteStatusResponse:
        count = await self._com_repo.cancelar_lote(lote_id)
        await self._auditar(
            actor_id=user_id,
            accion=COMUNICACION_ENVIAR,
            detalle={
                "accion": "cancelar_lote",
                "lote_id": str(lote_id),
                "afectadas": count,
                "motivo": motivo,
            },
        )
        await self._session.commit()
        return await self.get_lote_status(lote_id)

    async def cancelar_individual(
        self, id: uuid.UUID, user_id: uuid.UUID, motivo: str | None = None,
    ) -> ComunicacionDTO:
        com = await self._com_repo.get(id)
        if com is None:
            raise ValueError(f"Comunicación {id} no encontrada")

        validate_transition(com.estado, "Cancelado")
        com.estado = "Cancelado"
        await self._com_repo.update(com)

        await self._auditar(
            actor_id=user_id,
            accion=COMUNICACION_ENVIAR,
            detalle={
                "accion": "cancelar_individual",
                "comunicacion_id": str(id),
                "motivo": motivo,
            },
        )
        await self._session.commit()
        return _comunicacion_to_dto(com)

    async def get_lote_status(self, lote_id: uuid.UUID) -> LoteStatusResponse:
        comunicaciones = await self._com_repo.get_by_lote(lote_id)
        dtos = [_comunicacion_to_dto(c) for c in comunicaciones]
        resumen = self._build_resumen(comunicaciones)
        return LoteStatusResponse(
            lote_id=lote_id,
            comunicaciones=dtos,
            resumen=resumen,
        )

    async def get_by_materia(
        self, materia_id: uuid.UUID, estado: str | None = None,
    ) -> list[ComunicacionDTO]:
        comunicaciones = await self._com_repo.get_by_materia(materia_id, estado=estado)
        return [_comunicacion_to_dto(c) for c in comunicaciones]

    def _build_resumen(
        self, comunicaciones: list[Comunicacion],
    ) -> dict[str, int]:
        resumen: dict[str, int] = {
            "pendientes": 0,
            "enviados": 0,
            "errores": 0,
            "cancelados": 0,
        }
        for c in comunicaciones:
            estado = c.estado.lower()
            if estado == "pendiente":
                resumen["pendientes"] += 1
            elif estado == "enviado":
                resumen["enviados"] += 1
            elif estado == "error":
                resumen["errores"] += 1
            elif estado == "cancelado":
                resumen["cancelados"] += 1
        return resumen

    async def _auditar(
        self,
        actor_id: uuid.UUID,
        accion: str,
        detalle: dict | None = None,
    ) -> None:
        record = AuditLog(
            actor_id=actor_id,
            tenant_id=self._tenant_id,
            accion=accion,
            detalle=detalle,
            filas_afectadas=1,
        )
        await self._audit_repo.create(record)
