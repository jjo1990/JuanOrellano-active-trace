import csv
import io
import logging
import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.guardia import Guardia
from app.repositories.guardia_repository import GuardiaRepository
from app.schemas.guardia import GuardiaCreateRequest, GuardiaResponse, GuardiaUpdateRequest

logger = logging.getLogger(__name__)

CSV_HEADERS = [
    "Materia", "Carrera", "Cohorte", "Tutor", "Dia",
    "Horario", "Estado", "Comentarios", "Fecha de registro",
]


class GuardiaService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id
        self._repo = GuardiaRepository(session, tenant_id)

    async def registrar(
        self, data: GuardiaCreateRequest, tenant_id: uuid.UUID, user_id: uuid.UUID,
    ) -> Guardia:
        guardia = Guardia(
            asignacion_id=data.asignacion_id,
            materia_id=data.materia_id,
            carrera_id=data.carrera_id,
            cohorte_id=data.cohorte_id,
            dia=data.dia,
            horario=data.horario,
            estado=data.estado,
            comentarios=data.comentarios,
        )
        guardia = await self._repo.create(guardia)
        return guardia

    async def editar(
        self, guardia_id: uuid.UUID, data: GuardiaUpdateRequest,
        tenant_id: uuid.UUID, user_id: uuid.UUID,
    ) -> Guardia:
        guardia = await self._repo.get(guardia_id)
        if guardia is None:
            raise HTTPException(status_code=404, detail="Guardia no encontrada.")
        if data.estado is not None:
            guardia.estado = data.estado
        if data.horario is not None:
            guardia.horario = data.horario
        if data.comentarios is not None:
            guardia.comentarios = data.comentarios
        await self._session.flush()
        return guardia

    async def listar(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        estado: str | None = None,
    ) -> list[GuardiaResponse]:
        results = await self._repo.list_with_filters(
            tenant_id,
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            estado=estado,
        )
        return [
            GuardiaResponse(
                id=g.id,
                materia_id=g.materia_id,
                carrera_id=g.carrera_id,
                cohorte_id=g.cohorte_id,
                asignacion_id=g.asignacion_id,
                dia=g.dia,
                horario=g.horario,
                estado=g.estado,
                comentarios=g.comentarios,
                creada_at=g.created_at,
            )
            for g in results
        ]

    async def exportar_csv(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        estado: str | None = None,
    ) -> str:
        results = await self._repo.list_with_filters(
            tenant_id,
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            estado=estado,
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(CSV_HEADERS)

        for g in results:
            writer.writerow([
                str(g.materia_id),
                str(g.carrera_id),
                str(g.cohorte_id),
                str(g.asignacion_id),
                g.dia,
                g.horario,
                g.estado,
                g.comentarios or "",
                g.created_at.isoformat() if g.created_at else "",
            ])

        return output.getvalue()
