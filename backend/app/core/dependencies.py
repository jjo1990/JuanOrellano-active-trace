from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import create_session_factory
from app.core.exceptions import TokenExpiredError, TokenInvalidError
from app.core.security import verify_access_token
from app.schemas.auth import UserInfo

_security_scheme = HTTPBearer()


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        yield session


def get_tenant_from_header(
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
) -> UUID:
    if x_tenant_id is None:
        raise HTTPException(
            status_code=400,
            detail="X-Tenant-ID header es requerido para determinar el tenant.",
        )
    try:
        return UUID(x_tenant_id)
    except ValueError as exc:
        msg = "X-Tenant-ID debe ser un UUID válido."
        raise HTTPException(status_code=400, detail=msg) from exc


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_security_scheme),
) -> UserInfo:
    token = credentials.credentials
    try:
        payload = verify_access_token(token)
    except TokenExpiredError as exc:
        raise HTTPException(status_code=401, detail="Token expirado.") from exc
    except TokenInvalidError as exc:
        raise HTTPException(status_code=401, detail="Token inválido.") from exc

    sub = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    roles = payload.get("roles", [])

    if sub is None or tenant_id is None:
        raise HTTPException(status_code=401, detail="Token sin claims requeridos.")

    return UserInfo(
        id=UUID(sub),
        tenant_id=UUID(tenant_id),
        email="",
        display_name="",
        roles=roles,
    )


async def get_tenant_from_jwt(
    current_user: UserInfo = Depends(get_current_user),
) -> UUID:
    return current_user.tenant_id
