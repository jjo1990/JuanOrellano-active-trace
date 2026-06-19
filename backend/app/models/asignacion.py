import uuid
from datetime import date

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class Asignacion(BaseModelMixin, Base):
    __tablename__ = "asignacion"

    __table_args__ = (
        sa.Index("ix_asignacion_tenant_usuario", "tenant_id", "usuario_id"),
        sa.Index("ix_asignacion_tenant_rol", "tenant_id", "rol_id"),
        sa.Index("ix_asignacion_tenant_materia", "tenant_id", "materia_id"),
    )

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False,
    )
    rol_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("rol.id"), nullable=False,
    )
    materia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("materia.id"), nullable=True,
    )
    carrera_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("carrera.id"), nullable=True,
    )
    cohorte_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("cohorte.id"), nullable=True,
    )
    comisiones: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default=sa.text("'[]'::jsonb"), default=list,
    )
    responsable_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=True,
    )
    desde: Mapped[date] = mapped_column(sa.Date, nullable=False)
    hasta: Mapped[date | None] = mapped_column(sa.Date, nullable=True)

    usuario = relationship("User", lazy="selectin", foreign_keys=[usuario_id])
    rol = relationship("Rol", lazy="selectin", foreign_keys=[rol_id])
    materia = relationship("Materia", lazy="selectin", foreign_keys=[materia_id])
    carrera = relationship("Carrera", lazy="selectin", foreign_keys=[carrera_id])
    cohorte = relationship("Cohorte", lazy="selectin", foreign_keys=[cohorte_id])
