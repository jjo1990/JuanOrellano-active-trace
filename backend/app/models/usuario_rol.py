import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class UsuarioRol(BaseModelMixin, Base):
    __tablename__ = "usuario_rol"

    __table_args__ = (
        sa.UniqueConstraint("user_id", "rol_id", "fecha_desde", name="uq_usuario_rol"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False,
    )
    rol_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("rol.id"), nullable=False,
    )
    fecha_desde: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=False,
    )
    fecha_hasta: Mapped[datetime | None] = mapped_column(
        sa.TIMESTAMP(timezone=True), nullable=True,
    )
