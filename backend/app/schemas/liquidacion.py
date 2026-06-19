import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LiquidacionCalcularRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cohorte_id: uuid.UUID
    periodo: str = Field(min_length=7, max_length=7, pattern=r"^\d{4}-\d{2}$")


class LiquidacionCerrarRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cohorte_id: uuid.UUID
    periodo: str = Field(min_length=7, max_length=7, pattern=r"^\d{4}-\d{2}$")


class LiquidacionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID
    periodo: str
    usuario_id: uuid.UUID
    rol: str
    comisiones: list
    monto_base: float
    monto_plus: float
    total: float
    es_nexo: bool
    excluido_por_factura: bool
    estado: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class LiquidacionSegmentadaResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    general: list[LiquidacionResponse] = []
    nexo: list[LiquidacionResponse] = []
    facturantes: list[LiquidacionResponse] = []
    total_sin_factura: float = 0.0
    total_con_factura: float = 0.0
    advertencias: list[dict] = []


class LiquidacionCalcularResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    liquidaciones: list[LiquidacionResponse] = []
    advertencias: list[dict] = []


class LiquidacionCerrarResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cohorte_id: uuid.UUID
    periodo: str
    cantidad_cerradas: int
