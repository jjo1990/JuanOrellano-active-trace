import uuid
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.permiso import Permiso
from app.models.rol_permiso import RolPermiso
from app.models.usuario_rol import UsuarioRol


class PermissionService:
    """Resuelve permisos efectivos de un usuario en un tenant.

    Considera:
    1. Permisos heredados via UsuarioRol (legacy, histórico)
    2. Permisos heredados via Asignacion vigente (nuevo mecanismo)
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_effective_permissions(
        self, user_id: uuid.UUID, tenant_id: uuid.UUID,
    ) -> set[str]:
        ahora = datetime.now(timezone.utc)
        hoy = date.today()

        perms: set[str] = set()

        # 1. UsuarioRol (legacy)
        stmt_ur = (
            select(Permiso.codigo)
            .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
            .join(UsuarioRol, UsuarioRol.rol_id == RolPermiso.rol_id)
            .where(
                UsuarioRol.user_id == user_id,
                RolPermiso.tenant_id == tenant_id,
                UsuarioRol.tenant_id == tenant_id,
                UsuarioRol.fecha_desde <= ahora,
                (
                    (UsuarioRol.fecha_hasta.is_(None))
                    | (UsuarioRol.fecha_hasta >= ahora)
                ),
                Permiso.deleted_at.is_(None),
                RolPermiso.deleted_at.is_(None),
                UsuarioRol.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt_ur)
        perms.update(row[0] for row in result.fetchall())

        # 2. Asignacion vigente
        stmt_asig = (
            select(Permiso.codigo)
            .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
            .join(Asignacion, Asignacion.rol_id == RolPermiso.rol_id)
            .where(
                Asignacion.usuario_id == user_id,
                Asignacion.tenant_id == tenant_id,
                RolPermiso.tenant_id == tenant_id,
                Asignacion.desde <= hoy,
                (Asignacion.hasta.is_(None)) | (Asignacion.hasta >= hoy),
                Permiso.deleted_at.is_(None),
                RolPermiso.deleted_at.is_(None),
                Asignacion.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt_asig)
        perms.update(row[0] for row in result.fetchall())

        return perms
