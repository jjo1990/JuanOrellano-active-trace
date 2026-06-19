## 1. Action Codes y Permiso

- [x] 1.1 Agregar `AUDITORIA_VER = "auditoria:ver"` en `core/action_codes.py`
- [x] 1.2 Migración de datos: insertar `auditoria:ver` + RolPermiso (ADMIN, COORDINADOR). Idempotente.

## 2. Schemas

- [x] 2.1 Crear `schemas/auditoria.py`:
  - `PanelResponse`: acciones_por_dia, estado_comunicaciones, interacciones_docente_materia, ultimas_acciones
  - `PanelFilterParams`: fecha_desde, fecha_hasta, materia_id, usuario_id, limite
  - `LogEntryResponse`: fecha_hora, actor_id, materia_id, accion, filas_afectadas, ip, user_agent, detalle
  - `LogFilterParams`: fecha_desde, fecha_hasta, materia_id, usuario_id, accion, limite, offset
  - Todos `extra='forbid'`

## 3. Repository (extender)

- [x] 3.1 (RED+GREEN) Extender `repositories/audit_log.py` con métodos:
  - `list_with_filters(tenant_id, filters) -> Sequence[AuditLog]`
  - `count_by_date(tenant_id, desde, hasta, materia_ids) -> list[dict]`
  - `count_by_docente_accion(tenant_id, desde, hasta, materia_ids) -> list[dict]`
  - Tests: `tests/test_auditoria_repository.py`

## 4. Service

- [x] 4.1 (RED+GREEN) `services/auditoria_service.py`:
  - `get_panel(tenant_id, filters, user_id, is_admin) -> PanelResponse`
  - `get_log(tenant_id, filters, user_id, is_admin) -> list[LogEntryResponse]`
  - Scope propio: si no es admin, filtrar por materia_ids del usuario
  - Tests: `tests/test_auditoria_service.py`

## 5. Router

- [x] 5.1 `api/v1/routers/auditoria.py`:
  - `GET /api/auditoria/panel` → PanelResponse. Guard: `auditoria:ver`
  - `GET /api/auditoria/log` → list[LogEntryResponse]. Guard: `auditoria:ver`
- [x] 5.2 Registrar en `main.py`

## 6. Verificación

- [x] 6.1 `pytest` verde
- [x] 6.2 Cobertura ≥80%
- [x] 6.3 `extra='forbid'`, soft delete N/A (read-only), identidad JWT, sin hard delete
