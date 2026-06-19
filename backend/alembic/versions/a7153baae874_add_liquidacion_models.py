"""add liquidacion models

Revision ID: a7153baae874
Revises: 020
Create Date: 2026-06-18 20:29:47.787631
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'a7153baae874'
down_revision: Union[str, None] = '020'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('salario_base',
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('rol', sa.Enum('PROFESOR', 'TUTOR', 'NEXO', 'COORDINADOR', name='rol_salario_enum'), nullable=False),
    sa.Column('monto', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('desde', sa.Date(), nullable=False),
    sa.Column('hasta', sa.Date(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_salario_base_tenant_rol', 'salario_base', ['tenant_id', 'rol'], unique=False)
    op.create_table('salario_plus',
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('grupo', sa.String(length=100), nullable=False),
    sa.Column('rol', sa.Enum('PROFESOR', 'TUTOR', 'NEXO', 'COORDINADOR', name='rol_salario_enum'), nullable=False),
    sa.Column('descripcion', sa.String(length=255), nullable=False),
    sa.Column('monto', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('desde', sa.Date(), nullable=False),
    sa.Column('hasta', sa.Date(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_salario_plus_tenant_grupo_rol', 'salario_plus', ['tenant_id', 'grupo', 'rol'], unique=False)
    op.create_table('factura',
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('usuario_id', sa.UUID(), nullable=False),
    sa.Column('periodo', sa.String(length=7), nullable=False),
    sa.Column('detalle', sa.Text(), nullable=False),
    sa.Column('referencia_archivo', sa.String(length=500), nullable=True),
    sa.Column('tamano_kb', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('estado', sa.Enum('PENDIENTE', 'ABONADA', name='estado_factura_enum'), nullable=False),
    sa.Column('cargada_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('abonada_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id'], ),
    sa.ForeignKeyConstraint(['usuario_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_factura_tenant_estado', 'factura', ['tenant_id', 'estado'], unique=False)
    op.create_index('ix_factura_tenant_periodo', 'factura', ['tenant_id', 'periodo'], unique=False)
    op.create_index('ix_factura_tenant_usuario', 'factura', ['tenant_id', 'usuario_id'], unique=False)
    op.create_table('liquidacion',
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('cohorte_id', sa.UUID(), nullable=False),
    sa.Column('periodo', sa.String(length=7), nullable=False),
    sa.Column('usuario_id', sa.UUID(), nullable=False),
    sa.Column('rol', sa.Enum('PROFESOR', 'TUTOR', 'NEXO', 'COORDINADOR', name='rol_salario_enum'), nullable=False),
    sa.Column('comisiones', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
    sa.Column('monto_base', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('monto_plus', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('total', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('es_nexo', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('excluido_por_factura', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('estado', sa.Enum('ABIERTA', 'CERRADA', name='estado_liquidacion_enum'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['cohorte_id'], ['cohorte.id'], ),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id'], ),
    sa.ForeignKeyConstraint(['usuario_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tenant_id', 'cohorte_id', 'periodo', 'usuario_id', name='uq_liquidacion_cohorte_periodo_usuario')
    )
    op.create_index('ix_liquidacion_tenant_cohorte_periodo', 'liquidacion', ['tenant_id', 'cohorte_id', 'periodo'], unique=False)
    op.create_index('ix_liquidacion_tenant_usuario', 'liquidacion', ['tenant_id', 'usuario_id'], unique=False)
    op.add_column('materia', sa.Column('grupo_plus', sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column('materia', 'grupo_plus')
    op.drop_index('ix_liquidacion_tenant_usuario', table_name='liquidacion')
    op.drop_index('ix_liquidacion_tenant_cohorte_periodo', table_name='liquidacion')
    op.drop_table('liquidacion')
    op.drop_index('ix_factura_tenant_usuario', table_name='factura')
    op.drop_index('ix_factura_tenant_periodo', table_name='factura')
    op.drop_index('ix_factura_tenant_estado', table_name='factura')
    op.drop_table('factura')
    op.drop_index('ix_salario_plus_tenant_grupo_rol', table_name='salario_plus')
    op.drop_table('salario_plus')
    op.drop_index('ix_salario_base_tenant_rol', table_name='salario_base')
    op.drop_table('salario_base')
