import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VersionPadronDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    cargado_por: uuid.UUID
    cargado_at: datetime
    activa: bool


class EntradaPadronDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    version_id: uuid.UUID
    usuario_id: uuid.UUID | None = None
    nombre: str
    apellidos: str
    email: str | None = None
    comision: str | None = None
    regional: str | None = None


class ImportPreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preview_token: str
    filename: str
    detected_rows: int
    columns: list[str]
    preview_rows: list[dict]


class ConfirmResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version_id: uuid.UUID
    entries_count: int
    materia_id: uuid.UUID
    cohorte_id: uuid.UUID
    cargado_at: datetime


class VaciarResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    filas_afectadas: int
    mensaje: str
