from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RemitenteInfo(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: uuid.UUID
    nombre: str
    apellidos: str


class DestinatarioInfo(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: uuid.UUID
    nombre: str
    apellidos: str


class MensajeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    destinatario_id: uuid.UUID
    asunto: str = Field(min_length=1)
    cuerpo: str = Field(min_length=1)


class MensajeReplyCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cuerpo: str = Field(min_length=1)


class MensajeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    remitente: RemitenteInfo | None = None
    destinatario: DestinatarioInfo | None = None
    asunto: str
    cuerpo: str
    mensaje_padre_id: uuid.UUID | None = None
    leido: bool = False
    created_at: datetime | None = None


class ThreadListItem(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    remitente: RemitenteInfo | None = None
    asunto: str
    cuerpo: str
    leido: bool = False
    cantidad_respuestas: int = 0
    ultima_respuesta_at: datetime | None = None
    created_at: datetime | None = None


class ThreadDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mensaje_raiz: MensajeResponse
    respuestas: list[MensajeResponse] = []
