from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str
    apellidos: str
    email: EmailStr
    password: str = Field(min_length=8)
    dni: str | None = None
    cuil: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    banco: str | None = None
    regional: str | None = None
    legajo: str | None = None
    legajo_profesional: str | None = None
    facturador: bool = False
    activo: bool = True


class UsuarioUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str | None = None
    apellidos: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)
    dni: str | None = None
    cuil: str | None = None
    cbu: str | None = None
    alias_cbu: str | None = None
    banco: str | None = None
    regional: str | None = None
    legajo: str | None = None
    legajo_profesional: str | None = None
    facturador: bool | None = None


class UsuarioStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    activo: bool


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    nombre: str
    apellidos: str
    email: str
    banco: str | None = None
    regional: str | None = None
    legajo: str | None = None
    legajo_profesional: str | None = None
    facturador: bool
    activo: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def display_name(self) -> str:
        return f"{self.nombre} {self.apellidos}"
