from __future__ import annotations

import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MisEquiposResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    usuario_nombre: str
    usuario_apellidos: str
    usuario_email: str
    usuario_legajo: str | None = None
    rol_nombre: str
    materia_nombre: str | None = None
    carrera_nombre: str | None = None
    cohorte_nombre: str | None = None
    comisiones: list[str]
    desde: date
    hasta: date | None = None
    estado_vigencia: str


class MisEquiposFilterParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vigente: bool | None = None
    materia_id: uuid.UUID | None = None
    rol_id: uuid.UUID | None = None
    carrera_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None


class UsuarioBulkItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID


class AsignacionMasivaRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    usuarios: list[UsuarioBulkItem] = Field(min_length=1)
    materia_id: uuid.UUID | None = None
    carrera_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    rol_id: uuid.UUID
    comisiones: list[str] = []
    responsable_id: uuid.UUID | None = None
    desde: date
    hasta: date | None = None

    @model_validator(mode="after")
    def _validate_hasta_desde(self):
        if self.hasta is not None and self.desde and self.hasta < self.desde:
            raise ValueError("La fecha 'hasta' debe ser posterior o igual a 'desde'.")
        return self


class ErrorIndividual(BaseModel):
    model_config = ConfigDict(extra="forbid")

    usuario_id: uuid.UUID
    error: str


class AsignacionMasivaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asignaciones_creadas: list = []
    errores: list[ErrorIndividual] = []
    total_procesados: int
    total_exitosos: int
    total_fallidos: int


class ClonarEquipoRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID
    carrera_id: uuid.UUID
    cohorte_origen_id: uuid.UUID
    cohorte_destino_id: uuid.UUID
    desde: date
    hasta: date | None = None

    @model_validator(mode="after")
    def _validate_cohortes_diferentes(self):
        if self.cohorte_origen_id == self.cohorte_destino_id:
            raise ValueError("Las cohortes de origen y destino deben ser diferentes.")
        return self

    @model_validator(mode="after")
    def _validate_hasta_desde(self):
        if self.hasta is not None and self.desde and self.hasta < self.desde:
            raise ValueError("La fecha 'hasta' debe ser posterior o igual a 'desde'.")
        return self


class ClonarEquipoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asignaciones_creadas: list = []
    total_clonadas: int


class ModificarVigenciaRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID | None = None
    carrera_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    desde: date | None = None
    hasta: date | None = None

    @model_validator(mode="after")
    def _validate_al_menos_un_filtro(self):
        if not self.materia_id and not self.carrera_id and not self.cohorte_id:
            raise ValueError("Se requiere al menos un filtro: materia_id, carrera_id o cohorte_id.")
        return self

    @model_validator(mode="after")
    def _validate_hasta_desde(self):
        if self.desde is not None and self.hasta is not None and self.hasta < self.desde:
            raise ValueError("La fecha 'hasta' debe ser posterior o igual a 'desde'.")
        return self


class ModificarVigenciaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asignaciones_actualizadas: int
    total_encontradas: int


class ExportarEquipoParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    materia_id: uuid.UUID | None = None
    carrera_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    vigente: bool | None = None

    @model_validator(mode="after")
    def _validate_al_menos_un_filtro(self):
        if not self.materia_id and not self.carrera_id and not self.cohorte_id:
            raise ValueError("Se requiere al menos un filtro: materia_id, carrera_id o cohorte_id.")
        return self


class BuscarUsuariosParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    q: str
    limite: int = Field(default=20, ge=1)
    roles: str | None = None


class UsuarioAutocompletadoResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: uuid.UUID
    nombre: str
    apellidos: str
    email: str
    legajo: str | None = None
