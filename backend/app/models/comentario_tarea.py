import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import BaseModelMixin


class ComentarioTarea(BaseModelMixin, Base):
    __tablename__ = "comentario_tarea"

    __table_args__ = (
        sa.Index("ix_comentario_tarea_tenant_tarea", "tenant_id", "tarea_id"),
    )

    tarea_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tarea.id"), nullable=False,
    )
    autor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False,
    )
    texto: Mapped[str] = mapped_column(sa.Text, nullable=False)
