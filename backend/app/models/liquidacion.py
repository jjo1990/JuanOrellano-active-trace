import enum
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin
from app.models.salario_base import RolSalario


class EstadoLiquidacion(str, enum.Enum):
    ABIERTA = "Abierta"
    CERRADA = "Cerrada"


class Liquidacion(BaseModelMixin, Base):
    __tablename__ = "liquidacion"

    __table_args__ = (
        sa.Index("ix_liquidacion_tenant_cohorte_periodo", "tenant_id", "cohorte_id", "periodo"),
        sa.Index("ix_liquidacion_tenant_usuario", "tenant_id", "usuario_id"),
        sa.UniqueConstraint(
            "tenant_id", "cohorte_id", "periodo", "usuario_id",
            name="uq_liquidacion_cohorte_periodo_usuario",
        ),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False,
    )
    cohorte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("cohorte.id"), nullable=False,
    )
    periodo: Mapped[str] = mapped_column(sa.String(7), nullable=False)
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False,
    )
    rol: Mapped[RolSalario] = mapped_column(
        sa.Enum(RolSalario, name="rol_salario_enum", create_type=False), nullable=False,
    )
    comisiones: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default=sa.text("'[]'::jsonb"), default=list,
    )
    monto_base: Mapped[float] = mapped_column(sa.Numeric(12, 2), nullable=False)
    monto_plus: Mapped[float] = mapped_column(sa.Numeric(12, 2), nullable=False)
    total: Mapped[float] = mapped_column(sa.Numeric(12, 2), nullable=False)
    es_nexo: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.text("false"), default=False,
    )
    excluido_por_factura: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.text("false"), default=False,
    )
    estado: Mapped[EstadoLiquidacion] = mapped_column(
        sa.Enum(EstadoLiquidacion, name="estado_liquidacion_enum", create_type=True),
        nullable=False, default=EstadoLiquidacion.ABIERTA,
    )
