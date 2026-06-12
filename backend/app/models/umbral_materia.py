import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class UmbralMateria(BaseModelMixin, Base):
    __tablename__ = "umbral_materia"

    __table_args__ = (
        sa.UniqueConstraint(
            "asignacion_id", "materia_id", "tenant_id",
            name="uq_umbral_asignacion_materia",
        ),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False,
    )
    asignacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("asignacion.id"), nullable=False,
    )
    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=False,
    )
    umbral_pct: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, server_default="60", default=60,
    )
    valores_aprobatorios: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        server_default=sa.text("'[\"Satisfactorio\", \"Supera lo esperado\"]'::jsonb"),
        default=["Satisfactorio", "Supera lo esperado"],
    )
