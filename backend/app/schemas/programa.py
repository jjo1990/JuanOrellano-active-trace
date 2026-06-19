import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProgramaCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    materia_id: uuid.UUID
    carrera_id: uuid.UUID
    cohorte_id: uuid.UUID
    titulo: str
    referencia_archivo: str


class ProgramaUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    titulo: str | None = None
    referencia_archivo: str | None = None


class ProgramaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    materia_id: uuid.UUID
    carrera_id: uuid.UUID
    cohorte_id: uuid.UUID
    titulo: str
    referencia_archivo: str
    cargado_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
