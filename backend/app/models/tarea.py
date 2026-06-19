import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Tarea(BaseModelMixin, Base):
    __tablename__ = "tarea"

    __table_args__ = (
        sa.Index("ix_tarea_tenant_asignado_estado", "tenant_id", "asignado_a", "estado"),
        sa.Index("ix_tarea_tenant_materia", "tenant_id", "materia_id"),
        sa.Index("ix_tarea_tenant_estado", "tenant_id", "estado"),
    )

    materia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=True,
    )
    asignado_a: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False,
    )
    asignado_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False,
    )
    estado: Mapped[str] = mapped_column(
        sa.String(20),
        default="Pendiente",
        server_default=sa.text("'Pendiente'"),
        nullable=False,
    )
    descripcion: Mapped[str] = mapped_column(sa.Text, nullable=False)
    contexto_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True,
    )
