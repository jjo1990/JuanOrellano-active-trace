import uuid
from datetime import datetime
from typing import Sequence

from sqlalchemy import func, select

from app.models.reserva_evaluacion import ReservaEvaluacion
from app.repositories.base import Repository


class ReservaEvaluacionRepository(Repository[ReservaEvaluacion]):
    def __init__(self, session, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, ReservaEvaluacion)

    async def get_by_id(self, entity_id: uuid.UUID, tenant_id: uuid.UUID) -> ReservaEvaluacion | None:
        return await self.get(entity_id)

    async def list_by_evaluacion(
        self, evaluacion_id: uuid.UUID, tenant_id: uuid.UUID, estado: str | None = None,
    ) -> Sequence[ReservaEvaluacion]:
        filters = {"evaluacion_id": evaluacion_id}
        if estado is not None:
            filters["estado"] = estado
        return await self.list(**filters)

    async def list_by_alumno(self, alumno_id: uuid.UUID, tenant_id: uuid.UUID) -> Sequence[ReservaEvaluacion]:
        return await self.list(alumno_id=alumno_id)

    async def count_activas_por_fecha(self, evaluacion_id: uuid.UUID, fecha: datetime) -> int:
        start_of_day = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = fecha.replace(hour=23, minute=59, second=59, microsecond=999999)

        stmt = select(func.count()).where(
            self._model_class.evaluacion_id == evaluacion_id,
            self._model_class.tenant_id == self._tenant_id,
            self._model_class.estado == "Activa",
            self._model_class.fecha_hora >= start_of_day,
            self._model_class.fecha_hora <= end_of_day,
            self._model_class.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_activa_por_alumno_evaluacion(
        self, evaluacion_id: uuid.UUID, alumno_id: uuid.UUID,
    ) -> ReservaEvaluacion | None:
        stmt = select(self._model_class).where(
            self._model_class.evaluacion_id == evaluacion_id,
            self._model_class.alumno_id == alumno_id,
            self._model_class.tenant_id == self._tenant_id,
            self._model_class.estado == "Activa",
            self._model_class.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def cancelar(self, reserva_id: uuid.UUID) -> ReservaEvaluacion | None:
        reserva = await self.get(reserva_id)
        if reserva is None:
            return None
        reserva.estado = "Cancelada"
        await self._session.flush()
        return reserva
