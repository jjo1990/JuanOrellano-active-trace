"""seed liquidacion y factura permissions

Revision ID: d9b0414862fd
Revises: a7153baae874
Create Date: 2026-06-18 20:34:40.928520
"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd9b0414862fd'
down_revision: Union[str, None] = 'a7153baae874'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NUEVOS_PERMISOS = [
    ("liquidaciones:ver", "Ver liquidaciones calculadas", "liquidaciones"),
    ("liquidaciones:cerrar", "Cerrar liquidaciones de un período", "liquidaciones"),
    ("liquidaciones:configurar-salarios", "Configurar grilla salarial (base y plus)", "liquidaciones"),
]

PERMISOS_FINANZAS = [
    "liquidaciones:ver",
    "liquidaciones:cerrar",
    "liquidaciones:configurar-salarios",
]

PERMISOS_ADMIN = [
    "liquidaciones:ver",
]


def _get_rol_id(conn, nombre: str) -> str | None:
    meta = sa.MetaData()
    meta.reflect(bind=conn, only=("rol",))
    tbl = sa.Table("rol", meta)
    result = conn.execute(
        tbl.select().where(tbl.c.nombre == nombre, tbl.c.deleted_at.is_(None))
    ).first()
    return str(result._mapping["id"]) if result else None


def _get_permiso_id(conn, codigo: str) -> str | None:
    meta = sa.MetaData()
    meta.reflect(bind=conn, only=("permiso",))
    tbl = sa.Table("permiso", meta)
    result = conn.execute(
        tbl.select().where(tbl.c.codigo == codigo, tbl.c.deleted_at.is_(None))
    ).first()
    return str(result._mapping["id"]) if result else None


def upgrade() -> None:
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=conn, only=("permiso", "rol_permiso"))
    permiso_tbl = sa.Table("permiso", meta)
    rol_permiso_tbl = sa.Table("rol_permiso", meta)

    permiso_ids: dict[str, str] = {}

    for codigo, descripcion, modulo in NUEVOS_PERMISOS:
        existente = _get_permiso_id(conn, codigo)
        if existente:
            permiso_ids[codigo] = existente
        else:
            pid = str(uuid.uuid4())
            conn.execute(
                permiso_tbl.insert().values(
                    id=pid, codigo=codigo, descripcion=descripcion, modulo=modulo, tenant_id=None,
                )
            )
            permiso_ids[codigo] = pid

    finanzas_rol_id = _get_rol_id(conn, "FINANZAS")
    admin_rol_id = _get_rol_id(conn, "ADMIN")

    if finanzas_rol_id:
        for codigo in PERMISOS_FINANZAS:
            if codigo in permiso_ids:
                existente_rp = conn.execute(
                    rol_permiso_tbl.select().where(
                        rol_permiso_tbl.c.rol_id == finanzas_rol_id,
                        rol_permiso_tbl.c.permiso_id == permiso_ids[codigo],
                        rol_permiso_tbl.c.deleted_at.is_(None),
                    )
                ).first()
                if not existente_rp:
                    conn.execute(
                        rol_permiso_tbl.insert().values(
                            id=str(uuid.uuid4()),
                            rol_id=finanzas_rol_id,
                            permiso_id=permiso_ids[codigo],
                            tenant_id=None,
                        )
                    )

    if admin_rol_id:
        for codigo in PERMISOS_ADMIN:
            if codigo in permiso_ids:
                existente_rp = conn.execute(
                    rol_permiso_tbl.select().where(
                        rol_permiso_tbl.c.rol_id == admin_rol_id,
                        rol_permiso_tbl.c.permiso_id == permiso_ids[codigo],
                        rol_permiso_tbl.c.deleted_at.is_(None),
                    )
                ).first()
                if not existente_rp:
                    conn.execute(
                        rol_permiso_tbl.insert().values(
                            id=str(uuid.uuid4()),
                            rol_id=admin_rol_id,
                            permiso_id=permiso_ids[codigo],
                            tenant_id=None,
                        )
                    )


def downgrade() -> None:
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=conn, only=("permiso", "rol_permiso"))
    permiso_tbl = sa.Table("permiso", meta)
    rol_permiso_tbl = sa.Table("rol_permiso", meta)

    finanzas_rol_id = _get_rol_id(conn, "FINANZAS")
    admin_rol_id = _get_rol_id(conn, "ADMIN")

    for codigo, _, _ in NUEVOS_PERMISOS:
        pid = _get_permiso_id(conn, codigo)
        if pid is None:
            continue

        if finanzas_rol_id:
            conn.execute(
                rol_permiso_tbl.delete().where(
                    rol_permiso_tbl.c.rol_id == finanzas_rol_id,
                    rol_permiso_tbl.c.permiso_id == pid,
                )
            )
        if admin_rol_id:
            conn.execute(
                rol_permiso_tbl.delete().where(
                    rol_permiso_tbl.c.rol_id == admin_rol_id,
                    rol_permiso_tbl.c.permiso_id == pid,
                )
            )

        conn.execute(
            permiso_tbl.delete().where(permiso_tbl.c.id == pid)
        )
