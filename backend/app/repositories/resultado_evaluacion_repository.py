import uuid
from typing import Sequence

from sqlalchemy import select

from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.repositories.base import Repository


class ResultadoEvaluacionRepository(Repository[ResultadoEvaluacion]):
    def __init__(self, session, tenant_id: uuid.UUID) -> None:
        super().__init__(session, tenant_id, ResultadoEvaluacion)

    async def get_by_id(self, entity_id: uuid.UUID, tenant_id: uuid.UUID) -> ResultadoEvaluacion | None:
        return await self.get(entity_id)

    async def list_by_evaluacion(
        self, evaluacion_id: uuid.UUID, tenant_id: uuid.UUID,
    ) -> Sequence[ResultadoEvaluacion]:
        return await self.list(evaluacion_id=evaluacion_id)

    async def get_by_alumno_evaluacion(
        self, evaluacion_id: uuid.UUID, alumno_id: uuid.UUID,
    ) -> ResultadoEvaluacion | None:
        stmt = select(self._model_class).where(
            self._model_class.evaluacion_id == evaluacion_id,
            self._model_class.alumno_id == alumno_id,
            self._model_class.tenant_id == self._tenant_id,
            self._model_class.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_pendientes(
        self, tenant_id: uuid.UUID, materia_id: uuid.UUID | None = None,
    ) -> Sequence[ResultadoEvaluacion]:
        return await self.list(nota_final=None)

    async def batch_create(self, resultados: list[ResultadoEvaluacion]) -> list[ResultadoEvaluacion]:
        for r in resultados:
            r.tenant_id = self._tenant_id
            self._session.add(r)
        await self._session.flush()
        return resultados
