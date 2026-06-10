## Why

C-04 (RBAC) estableció la base de autorización con roles y permisos finos. El principio "todo audita" exige que cada acción significativa quede registrada en un log inmutable, atribuida a un actor real con timestamp y contexto. Sin audit log no hay trazabilidad, no hay accountability, y no se cumple el requisito fundacional del producto. Además, la impersonación (suplantación legítima para diagnóstico) requiere este log para registrar inicio/fin y atribuir acciones al actor real.

## What Changes

- **Modelo `AuditLog`** (E-AUD): tabla append-only con id, tenant_id, fecha_hora, actor_id, impersonado_id (nullable), materia_id (nullable), accion (código estandarizado), detalle (JSON), filas_afectadas, ip, user_agent
- **Trigger DB BEFORE UPDATE/DELETE** en `audit_log` como defensa en profundidad para garantizar inmutabilidad
- **AuditHelper**: función/clase utilitaria para registrar acciones con código estandarizado desde cualquier service
- **Permiso `impersonacion:usar`**: agregar al seed de permisos y a la matriz de ADMIN (y opcionalmente COORDINADOR)
- **Impersonación**: middleware/endpoints que permitan iniciar/finalizar impersonación, registrando `IMPERSONACION_INICIAR` / `IMPERSONACION_FINALIZAR` en el audit log
- **Migración 006**: creación de tabla `audit_log`, seed del permiso `impersonacion:usar`, trigger append-only
- **Tests**: append-only (update/delete rechazados), atribución bajo impersonación, registro con código + filas_afectadas

## Capabilities

### New Capabilities
- `audit-log`: registro inmutable de acciones significativas con código estandarizado, detalle JSON, y contexto de red (IP, user-agent). Defensa en profundidad: repositorio que solo expone create/list + trigger DB.
- `impersonation`: suplantación legítima de usuario para diagnóstico. Requiere permiso `impersonacion:usar`. Sesión distinguible. Acciones atribuidas al actor real. Inicio y fin registrados en audit log.

### Modified Capabilities

- *(ninguna — es la primera capacidad que se implementa sobre C-04)*

## Impact

- `backend/app/models/audit_log.py` — nuevo modelo SQLAlchemy
- `backend/app/repositories/audit_log.py` — nuevo repositorio (solo create + list)
- `backend/app/services/audit.py` — AuditHelper
- `backend/app/services/impersonation.py` — lógica de impersonación
- `backend/app/core/dependencies.py` — posible nueva dependencia para impersonación activa
- `backend/alembic/versions/006_audit_log.py` — migración + seed + trigger
- `backend/app/core/permissions.py` — registro del código `impersonacion:usar` si se centraliza
- `backend/app/models/permiso.py`, `backend/app/models/rol.py` — sin cambios (el seed es en migración)
- `backend/tests/` — tests para append-only, impersonación, audit helper
