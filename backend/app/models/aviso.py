import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Aviso(BaseModelMixin, Base):
    __tablename__ = "aviso"

    __table_args__ = (
        sa.Index("ix_aviso_tenant_alcance", "tenant_id", "alcance"),
        sa.Index("ix_aviso_tenant_activo", "tenant_id", "activo"),
    )

    alcance: Mapped[str] = mapped_column(sa.String(20), nullable=False)
    materia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=True,
    )
    cohorte_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("cohorte.id"), nullable=True,
    )
    rol_destino: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    severidad: Mapped[str] = mapped_column(
        sa.String(20), nullable=False, server_default="Info", default="Info",
    )
    titulo: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    cuerpo: Mapped[str] = mapped_column(sa.Text, nullable=False)
    inicio_en: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    fin_en: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    orden: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default="0", default=0)
    activo: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.text("true"), default=True)
    requiere_ack: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, server_default=sa.text("false"), default=False)
