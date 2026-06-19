import enum
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class EstadoFactura(str, enum.Enum):
    PENDIENTE = "Pendiente"
    ABONADA = "Abonada"


class Factura(BaseModelMixin, Base):
    __tablename__ = "factura"

    __table_args__ = (
        sa.Index("ix_factura_tenant_usuario", "tenant_id", "usuario_id"),
        sa.Index("ix_factura_tenant_estado", "tenant_id", "estado"),
        sa.Index("ix_factura_tenant_periodo", "tenant_id", "periodo"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False,
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False,
    )
    periodo: Mapped[str] = mapped_column(sa.String(7), nullable=False)
    detalle: Mapped[str] = mapped_column(sa.Text, nullable=False, default="")
    referencia_archivo: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    tamano_kb: Mapped[float | None] = mapped_column(sa.Numeric(10, 2), nullable=True)
    estado: Mapped[EstadoFactura] = mapped_column(
        sa.Enum(EstadoFactura, name="estado_factura_enum", create_type=True),
        nullable=False, default=EstadoFactura.PENDIENTE,
    )
    cargada_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False,
    )
    abonada_at: Mapped[datetime | None] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=True,
    )
