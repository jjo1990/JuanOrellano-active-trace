import uuid
from datetime import datetime, timezone
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.acknowledgment_aviso import AcknowledgmentAviso
from app.models.aviso import Aviso
from app.repositories.acknowledgment_aviso_repository import (
    AcknowledgmentAvisoRepository,
)
from app.repositories.asignacion_repository import AsignacionRepository
from app.repositories.aviso_repository import AvisoRepository
from app.schemas.aviso import (
    AvisoCreateRequest,
    AvisoResponse,
    AvisoUpdateRequest,
    AvisoVisibleResponse,
)


class AvisoService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._aviso_repo = AvisoRepository(session, tenant_id)
        self._ack_repo = AcknowledgmentAvisoRepository(session, tenant_id)
        self._asignacion_repo = AsignacionRepository(session, tenant_id)
        self._session = session
        self._tenant_id = tenant_id

    async def crear_aviso(self, data: AvisoCreateRequest, tenant_id: uuid.UUID) -> Aviso:
        aviso = Aviso(
            tenant_id=tenant_id,
            alcance=data.alcance,
            materia_id=data.materia_id,
            cohorte_id=data.cohorte_id,
            rol_destino=data.rol_destino,
            severidad=data.severidad,
            titulo=data.titulo,
            cuerpo=data.cuerpo,
            inicio_en=data.inicio_en,
            fin_en=data.fin_en,
            orden=data.orden,
            activo=data.activo,
            requiere_ack=data.requiere_ack,
        )
        created = await self._aviso_repo.create(aviso)
        await self._session.commit()
        await self._session.refresh(created)
        return created

    async def editar_aviso(
        self, id: uuid.UUID, data: AvisoUpdateRequest, tenant_id: uuid.UUID
    ) -> Aviso:
        aviso = await self._aviso_repo.get(id)
        if aviso is None:
            raise HTTPException(status_code=404, detail="Aviso no encontrado.")
        update_dict = data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(aviso, field, value)
        await self._aviso_repo.update(aviso)
        await self._session.commit()
        await self._session.refresh(aviso)
        return aviso

    async def get_aviso(self, id: uuid.UUID, tenant_id: uuid.UUID) -> Aviso:
        aviso = await self._aviso_repo.get(id)
        if aviso is None:
            raise HTTPException(status_code=404, detail="Aviso no encontrado.")
        return aviso

    async def list_avisos(self, tenant_id: uuid.UUID) -> Sequence[AvisoResponse]:
        avisos = await self._aviso_repo.list()
        responses = []
        for aviso in avisos:
            total_acks = await self._ack_repo.count_by_aviso(aviso.id)
            resp = AvisoResponse.model_validate(aviso)
            resp.total_acks = total_acks
            resp.total_vistas = 0
            responses.append(resp)
        return responses

    async def list_visibles(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID
    ) -> Sequence[AvisoVisibleResponse]:
        asignaciones = await self._asignacion_repo.list_by_usuario(user_id)
        materia_ids = {
            a.materia_id for a in asignaciones
            if a.materia_id is not None and a.deleted_at is None
        }
        cohorte_ids = {
            a.cohorte_id for a in asignaciones
            if a.cohorte_id is not None and a.deleted_at is None
        }

        from sqlalchemy import select, union
        from app.models.asignacion import Asignacion
        from app.models.rol import Rol
        from app.models.usuario_rol import UsuarioRol

        roles_directas = (
            select(Rol.nombre)
            .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
            .where(
                UsuarioRol.user_id == user_id,
                UsuarioRol.deleted_at.is_(None),
                Rol.deleted_at.is_(None),
            )
        )
        roles_asignaciones = (
            select(Rol.nombre)
            .join(Asignacion, Asignacion.rol_id == Rol.id)
            .where(
                Asignacion.usuario_id == user_id,
                Asignacion.deleted_at.is_(None),
                Rol.deleted_at.is_(None),
            )
        )
        combined = union(roles_directas, roles_asignaciones)
        result = await self._session.execute(combined)
        role_names = set(result.scalars().all())

        avisos = await self._aviso_repo.list_activos_en_ventana(tenant_id)
        ahora = datetime.now(timezone.utc)
        visibles = []

        for aviso in avisos:
            if aviso.activo is False:
                continue
            if aviso.inicio_en > ahora or aviso.fin_en < ahora:
                continue

            include = False
            if aviso.alcance == "Global":
                include = True
            elif aviso.alcance == "PorMateria":
                if aviso.materia_id in materia_ids:
                    include = True
            elif aviso.alcance == "PorCohorte":
                if aviso.cohorte_id in cohorte_ids:
                    include = True
            elif aviso.alcance == "PorRol":
                if aviso.rol_destino in role_names:
                    include = True

            if include:
                ya_confirmado = False
                if aviso.requiere_ack:
                    ack = await self._ack_repo.get_by_aviso_usuario(
                        aviso.id, user_id
                    )
                    ya_confirmado = ack is not None

                resp = AvisoVisibleResponse.model_validate(aviso)
                resp.ya_confirmado = ya_confirmado
                visibles.append(resp)

        return visibles

    async def acknowledge(
        self, aviso_id: uuid.UUID, tenant_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        aviso = await self._aviso_repo.get(aviso_id)
        if aviso is None:
            raise HTTPException(status_code=404, detail="Aviso no encontrado.")

        if not aviso.requiere_ack:
            return

        existing = await self._ack_repo.get_by_aviso_usuario(aviso_id, user_id)
        if existing is not None:
            return

        ack = AcknowledgmentAviso(
            aviso_id=aviso_id,
            usuario_id=user_id,
            tenant_id=tenant_id,
        )
        await self._ack_repo.create(ack)
        await self._session.commit()

    async def eliminar_aviso(self, id: uuid.UUID, tenant_id: uuid.UUID) -> None:
        aviso = await self._aviso_repo.get(id)
        if aviso is None:
            raise HTTPException(status_code=404, detail="Aviso no encontrado.")
        await self._aviso_repo.soft_delete(id)
        await self._session.commit()
