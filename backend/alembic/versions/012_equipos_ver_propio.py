"""C-08: insert permiso equipos:ver_propio + RolPermiso assignments

Revision ID: 012
Revises: 011
Create Date: 2026-06-15
"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "012"
down_revision: Union[str, None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PERMISO_CODIGO = "equipos:ver_propio"
PERMISO_DESCRIPCION = "Ver sus propios equipos docentes"
PERMISO_MODULO = "equipos"

ROLES_QUE_RECIBEN = ["PROFESOR", "TUTOR", "NEXO", "COORDINADOR"]


def _get_tables():
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=conn, only=("permiso", "rol", "rol_permiso"))
    return (
        sa.Table("permiso", meta),
        sa.Table("rol", meta),
        sa.Table("rol_permiso", meta),
    )


def upgrade() -> None:
    permiso_tbl, rol_tbl, rp_tbl = _get_tables()
    conn = op.get_bind()

    exists = conn.execute(
        permiso_tbl.select().where(permiso_tbl.c.codigo == PERMISO_CODIGO)
    ).first()
    if exists is not None:
        return

    permiso_id = str(uuid.uuid4())
    conn.execute(
        permiso_tbl.insert().values(
            id=permiso_id,
            codigo=PERMISO_CODIGO,
            descripcion=PERMISO_DESCRIPCION,
            modulo=PERMISO_MODULO,
            tenant_id=None,
        )
    )

    for rol_name in ROLES_QUE_RECIBEN:
        rol_row = conn.execute(
            rol_tbl.select().where(
                rol_tbl.c.nombre == rol_name,
                rol_tbl.c.tenant_id.is_(None),
            )
        ).first()
        if rol_row is None:
            continue
        rol_data = dict(rol_row._mapping)
        conn.execute(
            rp_tbl.insert().values(
                id=str(uuid.uuid4()),
                rol_id=rol_data["id"],
                permiso_id=permiso_id,
                tenant_id=None,
            )
        )


def downgrade() -> None:
    permiso_tbl, rol_tbl, rp_tbl = _get_tables()
    conn = op.get_bind()

    perm_row = conn.execute(
        permiso_tbl.select().where(permiso_tbl.c.codigo == PERMISO_CODIGO)
    ).first()
    if perm_row is None:
        return
    perm_data = dict(perm_row._mapping)

    conn.execute(
        rp_tbl.delete().where(rp_tbl.c.permiso_id == perm_data["id"])
    )
    conn.execute(
        permiso_tbl.delete().where(permiso_tbl.c.id == perm_data["id"])
    )
