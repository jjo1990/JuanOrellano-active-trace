"""C-14: create evaluacion, reserva_evaluacion, resultado_evaluacion + seed permisos

Revision ID: 014
Revises: 013
Create Date: 2026-06-16
"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "014"
down_revision: Union[str, None] = "013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PERMISOS = [
    {
        "codigo": "coloquios:gestionar",
        "descripcion": "Gestionar evaluaciones y coloquios",
        "modulo": "coloquios",
        "roles": ["COORDINADOR", "ADMIN"],
    },
    {
        "codigo": "coloquios:reservar",
        "descripcion": "Reservar turno en coloquio",
        "modulo": "coloquios",
        "roles": ["ALUMNO"],
    },
]


def upgrade() -> None:
    _create_evaluacion()
    _create_reserva_evaluacion()
    _create_resultado_evaluacion()
    _seed_permisos()


def downgrade() -> None:
    _remove_permisos()
    op.drop_table("resultado_evaluacion")
    op.drop_table("reserva_evaluacion")
    op.drop_table("evaluacion")


def _create_evaluacion() -> None:
    op.create_table(
        "evaluacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("materia_id", UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False),
        sa.Column("cohorte_id", UUID(as_uuid=True), sa.ForeignKey("cohorte.id"), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("instancia", sa.String(255), nullable=False),
        sa.Column("dias_disponibles", sa.Integer, nullable=False),
        sa.Column("cupos_por_dia", sa.Integer, nullable=False),
        sa.Column("estado", sa.String(20), server_default=sa.text("'Activa'"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_evaluacion_tenant_materia", "evaluacion", ["tenant_id", "materia_id"])
    op.create_index("ix_evaluacion_tenant_cohorte", "evaluacion", ["tenant_id", "cohorte_id"])
    op.create_index("ix_evaluacion_tenant_estado", "evaluacion", ["tenant_id", "estado"])


def _create_reserva_evaluacion() -> None:
    op.create_table(
        "reserva_evaluacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("evaluacion_id", UUID(as_uuid=True), sa.ForeignKey("evaluacion.id"), nullable=False),
        sa.Column("alumno_id", UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("fecha_hora", sa.DateTime(timezone=True), nullable=False),
        sa.Column("estado", sa.String(20), server_default=sa.text("'Activa'"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_reserva_eval_tenant_eval", "reserva_evaluacion", ["tenant_id", "evaluacion_id"])
    op.create_index("ix_reserva_eval_tenant_alumno", "reserva_evaluacion", ["tenant_id", "alumno_id"])
    op.create_index("ix_reserva_eval_tenant_estado", "reserva_evaluacion", ["tenant_id", "estado"])


def _create_resultado_evaluacion() -> None:
    op.create_table(
        "resultado_evaluacion",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=True),
        sa.Column("evaluacion_id", UUID(as_uuid=True), sa.ForeignKey("evaluacion.id"), nullable=False),
        sa.Column("alumno_id", UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("nota_final", sa.String(20), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_resultado_eval_tenant_eval", "resultado_evaluacion", ["tenant_id", "evaluacion_id"])
    op.create_index("ix_resultado_eval_tenant_alumno", "resultado_evaluacion", ["tenant_id", "alumno_id"])
    op.create_unique_constraint("uq_resultado_eval_eval_alumno", "resultado_evaluacion", ["evaluacion_id", "alumno_id"])


def _get_tables():
    conn = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=conn, only=("permiso", "rol", "rol_permiso"))
    return (
        sa.Table("permiso", meta),
        sa.Table("rol", meta),
        sa.Table("rol_permiso", meta),
    )


def _seed_permisos() -> None:
    permiso_tbl, rol_tbl, rp_tbl = _get_tables()
    conn = op.get_bind()

    for perm_data in PERMISOS:
        exists = conn.execute(
            permiso_tbl.select().where(permiso_tbl.c.codigo == perm_data["codigo"])
        ).first()
        if exists is not None:
            continue

        permiso_id = str(uuid.uuid4())
        conn.execute(
            permiso_tbl.insert().values(
                id=permiso_id,
                codigo=perm_data["codigo"],
                descripcion=perm_data["descripcion"],
                modulo=perm_data["modulo"],
                tenant_id=None,
            )
        )

        for rol_name in perm_data["roles"]:
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


def _remove_permisos() -> None:
    permiso_tbl, _rol_tbl, rp_tbl = _get_tables()
    conn = op.get_bind()

    for perm_data in PERMISOS:
        perm_row = conn.execute(
            permiso_tbl.select().where(permiso_tbl.c.codigo == perm_data["codigo"])
        ).first()
        if perm_row is None:
            continue
        perm_data_row = dict(perm_row._mapping)
        conn.execute(
            rp_tbl.delete().where(rp_tbl.c.permiso_id == perm_data_row["id"])
        )
        conn.execute(
            permiso_tbl.delete().where(permiso_tbl.c.id == perm_data_row["id"])
        )
