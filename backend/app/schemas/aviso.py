import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AvisoCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    alcance: str
    materia_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    rol_destino: str | None = None
    severidad: str = "Info"
    titulo: str
    cuerpo: str
    inicio_en: datetime
    fin_en: datetime
    orden: int = 0
    activo: bool = True
    requiere_ack: bool = False


class AvisoUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    alcance: str | None = None
    materia_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    rol_destino: str | None = None
    severidad: str | None = None
    titulo: str | None = None
    cuerpo: str | None = None
    inicio_en: datetime | None = None
    fin_en: datetime | None = None
    orden: int | None = None
    activo: bool | None = None
    requiere_ack: bool | None = None


class AvisoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    alcance: str
    materia_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    rol_destino: str | None = None
    severidad: str
    titulo: str
    cuerpo: str
    inicio_en: datetime
    fin_en: datetime
    orden: int
    activo: bool
    requiere_ack: bool
    total_vistas: int = 0
    total_acks: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class AvisoVisibleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    alcance: str
    materia_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    rol_destino: str | None = None
    severidad: str
    titulo: str
    cuerpo: str
    inicio_en: datetime
    fin_en: datetime
    orden: int
    activo: bool
    requiere_ack: bool
    ya_confirmado: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class AckResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mensaje: str
