import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Guardia(BaseModelMixin, Base):
    __tablename__ = "guardia"

    __table_args__ = (
        sa.Index("ix_guardia_tenant_materia", "tenant_id", "materia_id"),
        sa.Index("ix_guardia_tenant_asignacion", "tenant_id", "asignacion_id"),
    )

    asignacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("asignacion.id"), nullable=False,
    )
    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False,
    )
    carrera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("carrera.id"), nullable=False,
    )
    cohorte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("cohorte.id"), nullable=False,
    )
    dia: Mapped[str] = mapped_column(sa.String(10), nullable=False)
    horario: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    estado: Mapped[str] = mapped_column(
        sa.String(20), default="Pendiente", server_default=sa.text("'Pendiente'"), nullable=False,
    )
    comentarios: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
