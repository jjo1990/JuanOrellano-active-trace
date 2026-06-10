from collections.abc import AsyncGenerator, Callable
from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import create_session_factory
from app.core.exceptions import TokenExpiredError, TokenInvalidError
from app.core.permissions import PermissionService
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

    if sub is None or tenant_id is None:
        raise HTTPException(status_code=401, detail="Token sin claims requeridos.")

    return UserInfo(
        id=UUID(sub),
        tenant_id=UUID(tenant_id),
        email="",
        nombre="",
        apellidos="",
    )


async def resolve_impersonation(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(_security_scheme),
) -> None:
    """Detecta impersonación en el JWT y expone los datos en request.state.

    Uso: agregar como dependency en endpoints que necesiten saber
    si el usuario está impersonando a otro.

    Ej::

        @router.post("/recurso")
        async def handler(
            user = Depends(get_current_user),
            _ = Depends(resolve_impersonation),
            request: Request,
        ):
            actor = request.state.actor_id  # None si no impersona
    """
    token = credentials.credentials
    try:
        payload = verify_access_token(token)
    except Exception:
        request.state.impersonating = None
        request.state.actor_id = None
        return

    impersonating = payload.get("impersonating", False)
    if impersonating:
        request.state.impersonating = UUID(payload["sub"])
        request.state.actor_id = UUID(payload["actor_id"])
    else:
        request.state.impersonating = None
        request.state.actor_id = None


async def get_tenant_from_jwt(
    current_user: UserInfo = Depends(get_current_user),
) -> UUID:
    return current_user.tenant_id


class RequirePermission:
    """FastAPI dependency guard para permisos finos.

    Uso::

        @router.get("/calificaciones")
        async def listar(
            user = Depends(require_permission("calificaciones:importar")),
        ): ...

    Con context_check (permisos ``(propio)``)::

        @router.get("/calificaciones/{id}")
        async def ver(
            user = Depends(require_permission(
                "calificaciones:importar",
                context_check=lambda user, recurso_id: user.id == recurso_id,
            )),
        ): ...
    """

    def __init__(
        self,
        permiso: str,
        context_check: Callable[..., bool] | None = None,
    ) -> None:
        self._permiso = permiso
        self._context_check = context_check

    async def __call__(
        self,
        user: UserInfo = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> UserInfo:
        svc = PermissionService(db)
        perms = await svc.get_effective_permissions(user.id, user.tenant_id)
        if self._permiso not in perms:
            raise HTTPException(
                status_code=403,
                detail=f"Permiso requerido: {self._permiso}",
            )
        if self._context_check is not None and not self._context_check(user):
            raise HTTPException(
                status_code=403,
                detail="No tienes permiso sobre este recurso.",
            )
        return user


def require_permission(
    permiso: str,
    context_check: Callable[..., bool] | None = None,
) -> RequirePermission:
    """Retorna una dependency FastAPI que verifica que el usuario tenga el permiso.

    Args:
        permiso: Código del permiso requerido (e.g. ``"calificaciones:importar"``).
        context_check: Callable opcional para verificación adicional de contexto.
    """
    return RequirePermission(permiso, context_check=context_check)
