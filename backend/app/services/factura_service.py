import logging
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import action_codes
from app.models.audit_log import AuditLog
from app.models.factura import EstadoFactura, Factura
from app.models.user import User
from app.repositories.factura_repository import FacturaRepository
from app.schemas.factura import FacturaCreate, FacturaResponse, FacturaUpdate

logger = logging.getLogger(__name__)


class FacturaService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id
        self._repo = FacturaRepository(session, tenant_id)

    async def _run(self, coro):
        try:
            return await coro
        except IntegrityError as exc:
            await self._session.rollback()
            logger.warning("IntegrityError: %s", exc)
            raise HTTPException(
                status_code=409, detail="Conflicto de integridad."
            ) from exc

    async def _commit(self) -> None:
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            logger.warning("IntegrityError: %s", exc)
            raise HTTPException(
                status_code=409, detail="Conflicto de integridad."
            ) from exc

    async def _ensure_facturante(self, usuario_id: uuid.UUID) -> User:
        stmt = select(User).where(
            User.id == usuario_id,
            User.tenant_id == self._tenant_id,
            User.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        if not user.facturador:
            raise HTTPException(
                status_code=422,
                detail="El docente no está configurado como facturante.",
            )
        return user

    def _to_response(self, f: Factura) -> FacturaResponse:
        return FacturaResponse(
            id=f.id,
            tenant_id=f.tenant_id,
            usuario_id=f.usuario_id,
            periodo=f.periodo,
            detalle=f.detalle,
            referencia_archivo=f.referencia_archivo,
            tamano_kb=float(f.tamano_kb) if f.tamano_kb is not None else None,
            estado=f.estado.value,
            cargada_at=f.cargada_at,
            abonada_at=f.abonada_at,
            created_at=f.created_at,
            updated_at=f.updated_at,
        )

    def _log_audit(
        self,
        usuario_id: uuid.UUID,
        accion: str,
        detalle: dict | None = None,
    ) -> None:
        record = AuditLog(
            actor_id=usuario_id,
            tenant_id=self._tenant_id,
            accion=accion,
            detalle=detalle,
        )
        self._session.add(record)

    async def create(
        self, data: FacturaCreate, usuario_id: uuid.UUID,
    ) -> FacturaResponse:
        await self._ensure_facturante(data.usuario_id)

        factura = Factura(
            tenant_id=self._tenant_id,
            usuario_id=data.usuario_id,
            periodo=data.periodo,
            detalle=data.detalle,
            referencia_archivo=data.referencia_archivo,
            tamano_kb=data.tamano_kb,
            estado=EstadoFactura.PENDIENTE,
            cargada_at=datetime.now(timezone.utc),
        )
        self._session.add(factura)
        await self._session.flush()

        self._log_audit(usuario_id, action_codes.FACTURA_CARGAR, {
            "factura_id": str(factura.id),
            "usuario_id": str(data.usuario_id),
            "periodo": data.periodo,
        })
        await self._session.flush()
        return self._to_response(factura)

    async def get(self, id: uuid.UUID) -> FacturaResponse:
        f = await self._repo.get(id)
        if f is None:
            raise HTTPException(status_code=404, detail="Factura no encontrada.")
        return self._to_response(f)

    async def list_with_filters(
        self,
        usuario_id: uuid.UUID | None = None,
        estado: str | None = None,
        periodo: str | None = None,
    ) -> list[FacturaResponse]:
        results = await self._repo.list_with_filters(usuario_id, estado, periodo)
        return [self._to_response(f) for f in results]

    async def update(
        self, id: uuid.UUID, data: FacturaUpdate,
    ) -> FacturaResponse:
        f = await self._repo.get(id)
        if f is None:
            raise HTTPException(status_code=404, detail="Factura no encontrada.")

        update_dict = data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(f, field, value)

        result = await self._run(self._repo.update(f))
        await self._commit()
        return self._to_response(result)

    async def abonar(self, id: uuid.UUID, usuario_id: uuid.UUID) -> FacturaResponse:
        f = await self._repo.get(id)
        if f is None:
            raise HTTPException(status_code=404, detail="Factura no encontrada.")
        if f.estado == EstadoFactura.ABONADA:
            raise HTTPException(
                status_code=422, detail="La factura ya está abonada.",
            )

        f.estado = EstadoFactura.ABONADA
        f.abonada_at = datetime.now(timezone.utc)
        result = await self._run(self._repo.update(f))

        self._log_audit(usuario_id, action_codes.FACTURA_ABONAR, {
            "factura_id": str(result.id),
            "usuario_id": str(result.usuario_id),
        })
        await self._commit()
        return self._to_response(result)

    async def marcar_pendiente(
        self, id: uuid.UUID, usuario_id: uuid.UUID,
    ) -> FacturaResponse:
        f = await self._repo.get(id)
        if f is None:
            raise HTTPException(status_code=404, detail="Factura no encontrada.")
        if f.estado != EstadoFactura.ABONADA:
            raise HTTPException(
                status_code=422,
                detail="Solo facturas abonadas pueden marcarse como pendientes.",
            )

        f.estado = EstadoFactura.PENDIENTE
        f.abonada_at = None
        result = await self._run(self._repo.update(f))

        self._log_audit(
            usuario_id, action_codes.FACTURA_CARGAR,
            {"factura_id": str(result.id), "accion": "marcar_pendiente"},
        )
        await self._commit()
        return self._to_response(result)
