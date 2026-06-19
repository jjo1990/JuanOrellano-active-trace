import logging
import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mensaje import Mensaje
from app.models.user import User
from app.repositories.base import Repository
from app.repositories.mensaje_repository import MensajeRepository
from app.schemas.mensaje import (
    DestinatarioInfo,
    MensajeCreate,
    MensajeReplyCreate,
    MensajeResponse,
    RemitenteInfo,
    ThreadDetailResponse,
    ThreadListItem,
)

logger = logging.getLogger(__name__)


class MensajeService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._repo = MensajeRepository(session, tenant_id)
        self._user_repo = Repository(session, tenant_id, User)
        self._session = session
        self._tenant_id = tenant_id

    async def list_threads(self, user_id: uuid.UUID) -> list[ThreadListItem]:
        threads = await self._repo.list_threads_for_user(user_id)
        result = []
        for t in threads:
            count = await self._repo.count_respuestas(t.id)
            ultima = await self._repo.get_ultima_respuesta_at(t.id)
            result.append(
                ThreadListItem(
                    id=t.id,
                    remitente=RemitenteInfo(
                        id=t.remitente_id,
                        nombre="",
                        apellidos="",
                    ),
                    asunto=t.asunto,
                    cuerpo=t.cuerpo,
                    leido=t.leido,
                    cantidad_respuestas=count,
                    ultima_respuesta_at=ultima,
                    created_at=t.created_at,
                )
            )
        return result

    async def get_thread(
        self, mensaje_id: uuid.UUID, user_id: uuid.UUID,
    ) -> ThreadDetailResponse:
        can_access = await self._repo.user_can_access_thread(user_id, mensaje_id)
        if not can_access:
            raise HTTPException(status_code=404, detail="Hilo no encontrado.")

        root, replies = await self._repo.get_thread(mensaje_id)
        if root is None:
            raise HTTPException(status_code=404, detail="Hilo no encontrado.")

        if root.destinatario_id == user_id and not root.leido:
            root.leido = True
            await self._repo.update(root)
            await self._session.commit()
            await self._session.refresh(root)

        root_resp = MensajeResponse(
            id=root.id,
            tenant_id=root.tenant_id,
            remitente=RemitenteInfo(
                id=root.remitente_id, nombre="", apellidos="",
            ),
            destinatario=DestinatarioInfo(
                id=root.destinatario_id, nombre="", apellidos="",
            ),
            asunto=root.asunto,
            cuerpo=root.cuerpo,
            mensaje_padre_id=root.mensaje_padre_id,
            leido=root.leido,
            created_at=root.created_at,
        )

        replies_resp = []
        for r in replies:
            replies_resp.append(
                MensajeResponse(
                    id=r.id,
                    tenant_id=r.tenant_id,
                    remitente=RemitenteInfo(
                        id=r.remitente_id, nombre="", apellidos="",
                    ),
                    destinatario=DestinatarioInfo(
                        id=r.destinatario_id, nombre="", apellidos="",
                    ),
                    asunto=r.asunto,
                    cuerpo=r.cuerpo,
                    mensaje_padre_id=r.mensaje_padre_id,
                    leido=r.leido,
                    created_at=r.created_at,
                )
            )

        return ThreadDetailResponse(mensaje_raiz=root_resp, respuestas=replies_resp)

    async def create_message(
        self, data: MensajeCreate, remitente_id: uuid.UUID,
    ) -> MensajeResponse:
        destinatario = await self._user_repo.get(data.destinatario_id)
        if destinatario is None:
            raise HTTPException(status_code=404, detail="Destinatario no encontrado.")

        entity = Mensaje(
            remitente_id=remitente_id,
            destinatario_id=data.destinatario_id,
            asunto=data.asunto,
            cuerpo=data.cuerpo,
            mensaje_padre_id=None,
            leido=False,
        )
        result = await self._repo.create(entity)
        await self._session.commit()
        await self._session.refresh(result)

        return MensajeResponse(
            id=result.id,
            tenant_id=result.tenant_id,
            remitente=RemitenteInfo(id=result.remitente_id, nombre="", apellidos=""),
            destinatario=DestinatarioInfo(id=result.destinatario_id, nombre="", apellidos=""),
            asunto=result.asunto,
            cuerpo=result.cuerpo,
            mensaje_padre_id=result.mensaje_padre_id,
            leido=result.leido,
            created_at=result.created_at,
        )

    async def reply_to_thread(
        self,
        mensaje_id: uuid.UUID,
        data: MensajeReplyCreate,
        remitente_id: uuid.UUID,
    ) -> MensajeResponse:
        can_access = await self._repo.user_can_access_thread(remitente_id, mensaje_id)
        if not can_access:
            raise HTTPException(status_code=404, detail="Hilo no encontrado.")

        root, _ = await self._repo.get_thread(mensaje_id)
        if root is None:
            raise HTTPException(status_code=404, detail="Hilo no encontrado.")

        if root.remitente_id == remitente_id:
            destinatario_id = root.destinatario_id
        else:
            destinatario_id = root.remitente_id

        entity = Mensaje(
            remitente_id=remitente_id,
            destinatario_id=destinatario_id,
            asunto=root.asunto,
            cuerpo=data.cuerpo,
            mensaje_padre_id=mensaje_id,
            leido=False,
        )
        result = await self._repo.create(entity)
        await self._session.commit()
        await self._session.refresh(result)

        return MensajeResponse(
            id=result.id,
            tenant_id=result.tenant_id,
            remitente=RemitenteInfo(id=result.remitente_id, nombre="", apellidos=""),
            destinatario=DestinatarioInfo(id=result.destinatario_id, nombre="", apellidos=""),
            asunto=result.asunto,
            cuerpo=result.cuerpo,
            mensaje_padre_id=result.mensaje_padre_id,
            leido=result.leido,
            created_at=result.created_at,
        )
