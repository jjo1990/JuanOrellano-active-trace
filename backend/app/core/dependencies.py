from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import create_session_factory


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Dependency: yields a dedicated async session for the request.

    Session is automatically closed when the request finishes or
    when an exception propagates out of the handler.
    """
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        yield session


def get_tenant(request: Request) -> UUID:
    """Resuelve tenant_id desde el contexto de la request.

    En desarrollo lee X-Tenant-ID header. En producción (C-03) se
    reemplazará por extracción del JWT verificado.
    """
    tenant_id_str = request.headers.get("X-Tenant-ID")
    if tenant_id_str:
        return UUID(tenant_id_str)

    from app.core.exceptions import TenantNotFoundError

    raise TenantNotFoundError(
        "No tenant context. Set X-Tenant-ID header (development) "
        "or wait for C-03 JWT resolution."
    )


# ── Reserved slots (to be filled in later changes) ────────────────
# get_current_user → C-03  (JWT verification, returns AuthenticatedUser)
# require_permission → C-04 (RBAC: checks module:action against current user)
