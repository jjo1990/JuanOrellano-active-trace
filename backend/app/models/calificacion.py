import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Calificacion(BaseModelMixin, Base):
    __tablename__ = "calificacion"

    __table_args__ = (
        sa.CheckConstraint(
            "origen IN ('Importado', 'Manual')",
            name="ck_calificacion_origen",
        ),
        sa.Index("ix_calificacion_entrada_materia", "entrada_padron_id", "materia_id"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False,
    )
    entrada_padron_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("entrada_padron.id"), nullable=False,
    )
    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False,
    )
    actividad: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    nota_numerica: Mapped[float | None] = mapped_column(sa.Numeric(5, 2), nullable=True)
    nota_textual: Mapped[str | None] = mapped_column(sa.String(200), nullable=True)
    origen: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    importado_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False,
    )
