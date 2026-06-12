import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class VersionPadron(BaseModelMixin, Base):
    __tablename__ = "version_padron"

    __table_args__ = (
        sa.Index(
            "uq_version_padron_activa",
            "materia_id",
            "cohorte_id",
            "tenant_id",
            unique=True,
            postgresql_where=sa.text("activa = true"),
        ),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False,
    )
    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False,
    )
    cohorte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("cohorte.id"), nullable=False,
    )
    cargado_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False,
    )
    cargado_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False,
    )
    activa: Mapped[bool] = mapped_column(
        sa.Boolean, default=True, nullable=False,
    )
