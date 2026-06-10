import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RolCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nombre: str
    descripcion: str


class RolResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: uuid.UUID
    nombre: str
    descripcion: str
    tenant_id: uuid.UUID | None = None
    created_at: datetime | None = None
    deleted_at: datetime | None = None


class PermisoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: uuid.UUID
    codigo: str
    descripcion: str
    modulo: str


class RolPermisoAssign(BaseModel):
    model_config = ConfigDict(extra="forbid")
    permiso_id: uuid.UUID
