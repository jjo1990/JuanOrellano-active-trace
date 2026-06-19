## 1. Modelos SQLAlchemy

- [ ] 1.1 Crear `models/aviso.py` con modelo `Aviso(BaseModelMixin)`:
  - `__tablename__` = "aviso"
  - `alcance`: str (enum: Global/PorMateria/PorCohorte/PorRol), NOT NULL
  - `materia_id`: UUID FK → materia.id, nullable
  - `cohorte_id`: UUID FK → cohorte.id, nullable
  - `rol_destino`: str, nullable
  - `severidad`: str (enum: Info/Advertencia/Critico), default="Info"
  - `titulo`: str, NOT NULL
  - `cuerpo`: str, NOT NULL
  - `inicio_en`: datetime, NOT NULL
  - `fin_en`: datetime, NOT NULL
  - `orden`: int, default=0
  - `activo`: bool, default=True
  - `requiere_ack`: bool, default=False
  - `__table_args__`: Index en tenant_id+alcance, Index en tenant_id+activo

- [ ] 1.2 Crear `models/acknowledgment_aviso.py` con modelo `AcknowledgmentAviso(BaseModelMixin)`:
  - `__tablename__` = "acknowledgment_aviso"
  - `aviso_id`: UUID FK → aviso.id, NOT NULL
  - `usuario_id`: UUID FK → user.id, NOT NULL
  - `confirmado_at`: datetime, NOT NULL (default now)
  - `__table_args__`: UniqueConstraint(aviso_id, usuario_id), Index en tenant_id+aviso_id

- [ ] 1.3 Actualizar `models/__init__.py` para exportar Aviso, AcknowledgmentAviso

## 2. Migración Alembic

- [ ] 2.1 Generar migración: CREATE TABLE aviso, acknowledgment_aviso con FK, índices y constraints
- [ ] 2.2 Insertar permiso `avisos:publicar` + RolPermiso (COORDINADOR, ADMIN). Idempotente.
- [ ] 2.3 Verificar `alembic upgrade head` ejecuta sin error
- [ ] 2.4 Verificar `alembic downgrade -1` revierte correctamente

## 3. Action Codes

- [ ] 3.1 Agregar `AVISOS_PUBLICAR = "avisos:publicar"` en `core/action_codes.py`

## 4. Repositories

- [ ] 4.1 (RED) Escribir `tests/test_aviso_repository.py`: crear, listar activos, filtrar por alcance, soft delete
- [ ] 4.2 (GREEN) Implementar `repositories/aviso_repository.py`:
  - `AvisoRepository(Repository[Aviso])`
  - `list_activos_en_ventana(tenant_id) -> Sequence[Aviso]`
  - `list_by_alcance(tenant_id, alcance) -> Sequence[Aviso]`

- [ ] 4.3 (RED) Escribir `tests/test_acknowledgment_aviso_repository.py`: crear ack, duplicado ignora, contar por aviso
- [ ] 4.4 (GREEN) Implementar `repositories/acknowledgment_aviso_repository.py`:
  - `AcknowledgmentAvisoRepository(Repository[AcknowledgmentAviso])`
  - `get_by_aviso_usuario(aviso_id, usuario_id) -> AcknowledgmentAviso | None`
  - `count_by_aviso(aviso_id) -> int`
  - `count_acks_by_aviso(aviso_id) -> int`

## 5. Schemas Pydantic

- [ ] 5.1 Crear `schemas/aviso.py` con:
  - `AvisoCreateRequest`: alcance, materia_id (opc), cohorte_id (opc), rol_destino (opc), severidad, titulo, cuerpo, inicio_en, fin_en, orden (opc), activo (opc), requiere_ack (opc). `extra='forbid'`
  - `AvisoUpdateRequest`: todos opcionales excepto id. `extra='forbid'`
  - `AvisoResponse`: id + todos los campos + total_vistas, total_acks (derivados)
  - `AvisoVisibleResponse`: AvisoResponse simplificado (sin contadores)
  - `AckResponse`: mensaje (str)

## 6. Service

- [ ] 6.1 (RED) Escribir `tests/test_aviso_service.py`:
  - Crear aviso global con acuse
  - Crear aviso por materia
  - Listar avisos del publicador con contadores
  - Editar aviso (desactivar)
  - Consultar avisos visibles: filtra por RN-18 (ventana), RN-20 (alcance/rol), activo
  - Usuario ve solo avisos de su audiencia
  - Aviso fuera de ventana no aparece
  - Acusar recibo exitoso
  - Acuse duplicado idempotente
  - Contadores se actualizan

- [ ] 6.2 (GREEN) Implementar `services/aviso_service.py`:
  - `crear_aviso(data, tenant_id) -> Aviso`
  - `editar_aviso(id, data, tenant_id) -> Aviso`
  - `get_aviso(id, tenant_id) -> Aviso`
  - `list_avisos(tenant_id) -> list[AvisoResponse]` (con contadores)
  - `list_visibles(tenant_id, user_id) -> list[AvisoVisibleResponse]` (RN-18, RN-20)
  - `acknowledge(aviso_id, tenant_id, user_id) -> None` (RN-19)

## 7. Router

- [ ] 7.1 Implementar `api/v1/routers/avisos.py`:
  - `POST /api/avisos` → AvisoCreateRequest → AvisoResponse. Guard: `avisos:publicar`
  - `GET /api/avisos` → list[AvisoResponse]. Guard: `avisos:publicar`
  - `GET /api/avisos/{id}` → AvisoResponse
  - `PUT /api/avisos/{id}` → AvisoUpdateRequest → AvisoResponse. Guard: `avisos:publicar`
  - `DELETE /api/avisos/{id}` → 204. Guard: `avisos:publicar`
  - `GET /api/avisos/visibles` → list[AvisoVisibleResponse] (cualquier usuario autenticado)
  - `POST /api/avisos/{id}/ack` → AckResponse (cualquier usuario autenticado)

- [ ] 7.2 Registrar router en `main.py`

## 8. Tests y verificación

- [ ] 8.1 Tests de repositorio (aviso + acknowledgment)
- [ ] 8.2 Tests de servicio (avisos visibles, acuse, segmentación)
- [ ] 8.3 Ejecutar suite completa (`pytest`) verde
- [ ] 8.4 Cobertura ≥80% líneas, ≥90% reglas de negocio
- [ ] 8.5 Ningún archivo >500 LOC
- [ ] 8.6 Todos schemas con `extra='forbid'`
- [ ] 8.7 Sin hard delete
- [ ] 8.8 Identidad desde JWT, no desde params
