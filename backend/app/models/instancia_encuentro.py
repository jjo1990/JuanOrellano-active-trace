import uuid
from datetime import date, time

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class InstanciaEncuentro(BaseModelMixin, Base):
    __tablename__ = "instancia_encuentro"

    __table_args__ = (
        sa.Index("ix_inst_encuentro_tenant_slot", "tenant_id", "slot_id"),
        sa.Index("ix_inst_encuentro_tenant_materia", "tenant_id", "materia_id"),
        sa.Index("ix_inst_encuentro_tenant_estado", "tenant_id", "estado"),
    )

    slot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("slot_encuentro.id"), nullable=True,
    )
    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False,
    )
    fecha: Mapped[date] = mapped_column(sa.Date, nullable=False)
    hora: Mapped[time] = mapped_column(sa.Time, nullable=False)
    titulo: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    estado: Mapped[str] = mapped_column(
        sa.String(20), default="Programado", server_default=sa.text("'Programado'"), nullable=False,
    )
    meet_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    video_url: Mapped[str | None] = mapped_column(sa.String(500), nullable=True)
    comentario: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
