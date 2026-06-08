import uuid
from typing import Generic, Sequence, TypeVar

from sqlalchemy import func, select, update as sa_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RepositoryError
from app.models.mixins import BaseModelMixin

ModelT = TypeVar("ModelT", bound=BaseModelMixin)


class Repository(Generic[ModelT]):
    """Repositorio genérico con scope obligatorio de tenant.

    Toda operación filtra por tenant_id. El tenant se inyecta en el
    constructor para garantizar que ningún método lo omita.
    """

    def __init__(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        model_class: type[ModelT],
    ) -> None:
        self._session = session
        self._tenant_id = tenant_id
        self._model_class = model_class

    async def get(self, id: uuid.UUID) -> ModelT | None:
        stmt = select(self._model_class).where(
            self._model_class.id == id,
            self._model_class.tenant_id == self._tenant_id,
            self._model_class.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, **filters) -> Sequence[ModelT]:
        stmt = (
            select(self._model_class)
            .where(
                self._model_class.tenant_id == self._tenant_id,
                self._model_class.deleted_at.is_(None),
            )
            .order_by(self._model_class.created_at)
        )
        for attr, value in filters.items():
            column = getattr(self._model_class, attr, None)
            if column is not None:
                stmt = stmt.where(column == value)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create(self, entity: ModelT) -> ModelT:
        entity.tenant_id = self._tenant_id
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, entity: ModelT) -> ModelT:
        if entity.tenant_id != self._tenant_id:
            msg = "Entity does not belong to this tenant"
            raise RepositoryError(msg)
        merged = await self._session.merge(entity)
        await self._session.flush()
        return merged

    async def soft_delete(self, id: uuid.UUID) -> None:
        stmt = (
            sa_update(self._model_class)
            .where(
                self._model_class.id == id,
                self._model_class.tenant_id == self._tenant_id,
            )
            .values(deleted_at=func.now())
        )
        result = await self._session.execute(stmt)
        if result.rowcount == 0:
            msg = "Entity not found or does not belong to this tenant"
            raise RepositoryError(msg)
        await self._session.flush()
