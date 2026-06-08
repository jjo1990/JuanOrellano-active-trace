from collections.abc import AsyncGenerator

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


# ── Reserved slots (to be filled in later changes) ────────────────
#
# get_current_user → C-03  (JWT verification, returns AuthenticatedUser)
# get_tenant        → C-02  (resolves tenant_id from authenticated session)
# require_permission → C-04 (RBAC: checks module:action against current user)
