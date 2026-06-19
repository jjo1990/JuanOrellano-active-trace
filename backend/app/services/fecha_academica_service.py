import logging
import uuid
from collections import defaultdict

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fecha_academica import FechaAcademica
from app.repositories.fecha_academica_repository import FechaAcademicaRepository
from app.schemas.fecha_academica import FechaCreateRequest, FechaUpdateRequest

logger = logging.getLogger(__name__)


class FechaAcademicaService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._repo = FechaAcademicaRepository(session, tenant_id)
        self._session = session

    async def _commit(self) -> None:
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            logger.warning("IntegrityError: %s", exc)
            raise HTTPException(status_code=409, detail="El recurso ya existe o viola una restriccion de unicidad.") from exc

    async def _run(self, coro):
        try:
            result = await coro
            return result
        except IntegrityError as exc:
            await self._session.rollback()
            logger.warning("IntegrityError: %s", exc)
            raise HTTPException(status_code=409, detail="El recurso ya existe o viola una restriccion de unicidad.") from exc

    async def create(self, data: FechaCreateRequest) -> FechaAcademica:
        entity = FechaAcademica(
            materia_id=data.materia_id,
            cohorte_id=data.cohorte_id,
            tipo=data.tipo,
            numero=data.numero,
            periodo=data.periodo,
            fecha=data.fecha,
            titulo=data.titulo,
        )
        result = await self._run(self._repo.create(entity))
        await self._commit()
        await self._session.refresh(result)
        return result

    async def get(self, id: uuid.UUID) -> FechaAcademica | None:
        return await self._repo.get(id)

    async def list_with_filters(self, **filters) -> list[FechaAcademica]:
        result = await self._repo.list_with_filters(**filters)
        return list(result)

    async def get_calendario(self, cohorte_id: uuid.UUID) -> dict[str, list[FechaAcademica]]:
        fechas = await self._repo.list_by_cohorte(cohorte_id)
        grouped: dict[str, list[FechaAcademica]] = defaultdict(list)
        for f in fechas:
            key = f.fecha.strftime("%Y-%m")
            grouped[key].append(f)
        return dict(sorted(grouped.items()))

    async def generate_cronograma_html(self, materia_id: uuid.UUID, cohorte_id: uuid.UUID) -> str:
        fechas = await self._repo.list_with_filters(
            materia_id=materia_id, cohorte_id=cohorte_id,
        )
        grouped: dict[str, list[FechaAcademica]] = defaultdict(list)
        for f in fechas:
            grouped[f.tipo].append(f)

        tipo_order = ["Parcial", "TP", "Coloquio", "Recuperatorio"]
        html_parts = [
            "<table>",
            "<tr><th>Tipo</th><th>N°</th><th>Fecha</th><th>Titulo</th><th>Periodo</th></tr>",
        ]
        for tipo in tipo_order:
            items = grouped.get(tipo, [])
            for item in sorted(items, key=lambda x: x.fecha):
                html_parts.append(
                    f"<tr><td>{item.tipo}</td><td>{item.numero}</td>"
                    f"<td>{item.fecha.isoformat()}</td><td>{item.titulo}</td><td>{item.periodo}</td></tr>"
                )
        html_parts.append("</table>")
        return "\n".join(html_parts)

    async def update(self, id: uuid.UUID, data: FechaUpdateRequest) -> FechaAcademica:
        entity = await self._repo.get(id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Fecha academica no encontrada.")
        update_dict = data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(entity, field, value)
        result = await self._run(self._repo.update(entity))
        await self._commit()
        await self._session.refresh(result)
        return result

    async def delete(self, id: uuid.UUID) -> None:
        entity = await self._repo.get(id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Fecha academica no encontrada.")
        await self._run(self._repo.soft_delete(id))
        await self._commit()
