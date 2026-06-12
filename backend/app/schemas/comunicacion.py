import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ComunicacionDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    enviado_por: uuid.UUID
    materia_id: uuid.UUID
    destinatario: str
    asunto: str
    cuerpo: str
    estado: str
    lote_id: uuid.UUID | None = None
    enviado_at: datetime | None = None
    created_at: datetime


class PreviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    template: str
    alumno_ids: list[uuid.UUID]
    materia_id: uuid.UUID


class PreviewItemDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    alumno_id: uuid.UUID
    nombre: str
    asunto: str
    cuerpo: str


class PreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    previews: list[PreviewItemDTO]


class EnviarRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    template: str
    alumno_ids: list[uuid.UUID]
    materia_id: uuid.UUID
    asunto: str


class EnviarResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lote_id: uuid.UUID
    count: int
    estado: str


class LoteStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lote_id: uuid.UUID
    comunicaciones: list[ComunicacionDTO]
    resumen: dict[str, int]


class CancelarRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    motivo: str | None = None
