import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


ESTADOS_VALIDOS = {"Pendiente", "En progreso", "Resuelta", "Cancelada"}


class TareaCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    materia_id: uuid.UUID | None = None
    asignado_a: uuid.UUID
    descripcion: str
    contexto_id: uuid.UUID | None = None


class TareaUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    descripcion: str | None = None
    materia_id: uuid.UUID | None = None


class TareaDelegarRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nuevo_asignado_id: uuid.UUID


class TareaEstadoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    estado: str

    def estado_valido(self) -> bool:
        return self.estado in ESTADOS_VALIDOS


class ComentarioCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    texto: str = Field(min_length=1)


class ComentarioResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: uuid.UUID
    tarea_id: uuid.UUID
    autor_id: uuid.UUID
    texto: str
    created_at: datetime | None = None


class TareaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    materia_id: uuid.UUID | None = None
    asignado_a: uuid.UUID
    asignado_por: uuid.UUID
    estado: str
    descripcion: str
    contexto_id: uuid.UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    comentarios: list[ComentarioResponse] = []
