import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.repositories.base import Repository


class EstructuraRepository:
    """Repository unificado para Carrera, Cohorte y Materia.

    Delega operaciones CRUD al Repository genérico con scope de tenant.
    """

    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._carrera_repo: Repository[Carrera] = Repository(session, tenant_id, Carrera)
        self._cohorte_repo: Repository[Cohorte] = Repository(session, tenant_id, Cohorte)
        self._materia_repo: Repository[Materia] = Repository(session, tenant_id, Materia)
        self._session = session

    # ── Carrera ───────────────────────────────────────────────────────────

    async def create_carrera(self, entity: Carrera) -> Carrera:
        return await self._carrera_repo.create(entity)

    async def get_carrera(self, id: uuid.UUID) -> Carrera | None:
        return await self._carrera_repo.get(id)

    async def list_carreras(self, **filters) -> Sequence[Carrera]:
        return await self._carrera_repo.list(**filters)

    async def update_carrera(self, entity: Carrera) -> Carrera:
        return await self._carrera_repo.update(entity)

    async def soft_delete_carrera(self, id: uuid.UUID) -> None:
        await self._carrera_repo.soft_delete(id)

    # ── Cohorte ───────────────────────────────────────────────────────────

    async def create_cohorte(self, entity: Cohorte) -> Cohorte:
        return await self._cohorte_repo.create(entity)

    async def get_cohorte(self, id: uuid.UUID) -> Cohorte | None:
        return await self._cohorte_repo.get(id)

    async def list_cohortes(self, **filters) -> Sequence[Cohorte]:
        return await self._cohorte_repo.list(**filters)

    async def update_cohorte(self, entity: Cohorte) -> Cohorte:
        return await self._cohorte_repo.update(entity)

    async def soft_delete_cohorte(self, id: uuid.UUID) -> None:
        await self._cohorte_repo.soft_delete(id)

    # ── Materia ───────────────────────────────────────────────────────────

    async def create_materia(self, entity: Materia) -> Materia:
        return await self._materia_repo.create(entity)

    async def get_materia(self, id: uuid.UUID) -> Materia | None:
        return await self._materia_repo.get(id)

    async def list_materias(self, **filters) -> Sequence[Materia]:
        return await self._materia_repo.list(**filters)

    async def update_materia(self, entity: Materia) -> Materia:
        return await self._materia_repo.update(entity)

    async def soft_delete_materia(self, id: uuid.UUID) -> None:
        await self._materia_repo.soft_delete(id)

    async def list_materias_by_grupo_plus(self, grupo: str) -> Sequence[Materia]:
        stmt = (
            select(Materia)
            .where(
                Materia.tenant_id == self._materia_repo._tenant_id,
                Materia.deleted_at.is_(None),
                Materia.grupo_plus == grupo,
            )
            .order_by(Materia.created_at)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()
