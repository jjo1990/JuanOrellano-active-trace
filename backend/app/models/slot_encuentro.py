import uuid
from datetime import date, time

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class SlotEncuentro(BaseModelMixin, Base):
    __tablename__ = "slot_encuentro"

    __table_args__ = (
        sa.Index("ix_slot_encuentro_tenant_materia", "tenant_id", "materia_id"),
        sa.Index("ix_slot_encuentro_tenant_asignacion", "tenant_id", "asignacion_id"),
    )

    asignacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("asignacion.id"), nullable=False,
    )
    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False,
    )
    titulo: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    hora: Mapped[time] = mapped_column(sa.Time, nullable=False)
    dia_semana: Mapped[str | None] = mapped_column(sa.String(10), nullable=True)
    fecha_inicio: Mapped[date | None] = mapped_column(sa.Date, nullable=True)
    cant_semanas: Mapped[int] = mapped_column(sa.Integer, default=0, server_default=sa.text("0"), nullable=False)
    fecha_unica: Mapped[date | None] = mapped_column(sa.Date, nullable=True)
    meet_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
