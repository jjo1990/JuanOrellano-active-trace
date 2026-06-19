import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_permission
from app.schemas.auth import UserInfo
from app.schemas.factura import FacturaCreate, FacturaResponse, FacturaUpdate
from app.services.factura_service import FacturaService

router = APIRouter(prefix="/api/facturas", tags=["facturas"])


@router.post("", response_model=FacturaResponse, status_code=201)
async def create_factura(
    body: FacturaCreate,
    user: UserInfo = Depends(require_permission("facturas:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = FacturaService(db, user.tenant_id)
    return await svc.create(body, user.id)


@router.get("", response_model=list[FacturaResponse])
async def list_facturas(
    usuario_id: uuid.UUID | None = Query(None),
    estado: str | None = Query(None),
    periodo: str | None = Query(None, min_length=7, max_length=7),
    user: UserInfo = Depends(require_permission("facturas:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = FacturaService(db, user.tenant_id)
    return await svc.list_with_filters(usuario_id, estado, periodo)


@router.get("/{id}", response_model=FacturaResponse)
async def get_factura(
    id: uuid.UUID,
    user: UserInfo = Depends(require_permission("facturas:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = FacturaService(db, user.tenant_id)
    return await svc.get(id)


@router.put("/{id}", response_model=FacturaResponse)
async def update_factura(
    id: uuid.UUID,
    body: FacturaUpdate,
    user: UserInfo = Depends(require_permission("facturas:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = FacturaService(db, user.tenant_id)
    return await svc.update(id, body)


@router.post("/{id}/abonar", response_model=FacturaResponse)
async def abonar_factura(
    id: uuid.UUID,
    user: UserInfo = Depends(require_permission("facturas:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = FacturaService(db, user.tenant_id)
    return await svc.abonar(id, user.id)


@router.post("/{id}/marcar-pendiente", response_model=FacturaResponse)
async def marcar_pendiente(
    id: uuid.UUID,
    user: UserInfo = Depends(require_permission("facturas:gestionar")),
    db: AsyncSession = Depends(get_db),
):
    svc = FacturaService(db, user.tenant_id)
    return await svc.marcar_pendiente(id, user.id)
