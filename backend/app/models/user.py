import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.fields import EncryptedField
from app.models.mixins import BaseModelMixin


class User(BaseModelMixin, Base):
    __tablename__ = "user"

    __table_args__ = (
        sa.UniqueConstraint("email", "tenant_id", name="uq_user_email_tenant"),
        sa.Index("ix_user_email_tenant", "email", "tenant_id"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("tenant.id"), nullable=False,
    )
    email: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    totp_secret: Mapped[str | None] = mapped_column(sa.String(512), nullable=True)
    totp_enabled: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.text("false"), default=False,
    )

    # ── Información personal ──────────────────────────────────────────────
    nombre: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(sa.String(200), nullable=False)

    # ── PII cifrada (encrypted companion columns + descriptor) ────────────
    dni_encrypted: Mapped[str | None] = mapped_column(
        "dni_encrypted", sa.String(512), nullable=True,
    )
    dni = EncryptedField()

    cuil_encrypted: Mapped[str | None] = mapped_column(
        "cuil_encrypted", sa.String(512), nullable=True,
    )
    cuil = EncryptedField()

    cbu_encrypted: Mapped[str | None] = mapped_column(
        "cbu_encrypted", sa.String(512), nullable=True,
    )
    cbu = EncryptedField()

    alias_cbu_encrypted: Mapped[str | None] = mapped_column(
        "alias_cbu_encrypted", sa.String(512), nullable=True,
    )
    alias_cbu = EncryptedField()

    # ── Datos adicionales ─────────────────────────────────────────────────
    banco: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    regional: Mapped[str | None] = mapped_column(sa.String(100), nullable=True)
    legajo: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    legajo_profesional: Mapped[str | None] = mapped_column(sa.String(50), nullable=True)
    facturador: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.text("false"), default=False,
    )
    activo: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.text("true"), default=True,
    )
