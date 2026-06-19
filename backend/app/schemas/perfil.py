from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class PerfilUpdate(BaseModel):
    """Campos editables del perfil propio. Excluye CUIL, password, activo."""

    model_config = ConfigDict(extra="forbid")

    nombre: str | None = None
    apellidos: str | None = None
    dni: str | None = None
    banco: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    regional: str | None = None
    email: EmailStr | None = None
    legajo: str | None = None
    legajo_profesional: str | None = None
    facturador: bool | None = None


class PerfilResponse(BaseModel):
    """Respuesta completa del perfil propio, incluye PII descifrado."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    nombre: str
    apellidos: str
    email: str
    dni: str | None = None
    cuil: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    banco: str | None = None
    regional: str | None = None
    legajo: str | None = None
    legajo_profesional: str | None = None
    facturador: bool
    activo: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
