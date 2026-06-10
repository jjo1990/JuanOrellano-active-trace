## 1. Modelo AuditLog y action codes

- [x] 1.1 Crear `app/core/action_codes.py` con constantes: `CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`, `COMUNICACION_ENVIAR`, `ASIGNACION_MODIFICAR`, `LIQUIDACION_CERRAR`, `IMPERSONACION_INICIAR`, `IMPERSONACION_FINALIZAR`
- [x] 1.2 Crear modelo `AuditLog` en `app/models/audit_log.py` heredando de `BaseModelMixin`: campos id, tenant_id, fecha_hora, actor_id, impersonado_id (nullable), materia_id (nullable), accion, detalle (JSONB nullable), filas_afectadas, ip (nullable), user_agent (nullable)
- [x] 1.3 Crear repositorio `AuditLogRepository` en `app/repositories/audit_log.py` con métodos `create()` y `list()` (sin update, sin delete)
- [x] 1.4 Crear `AuditService` en `app/services/audit.py` con método `log(actor_id, tenant_id, accion, detalle=None, filas_afectadas=0, request=None, impersonado_id=None)` que use AuditLogRepository
- [x] 1.5 Registrar dependencia de `AuditService` en el contenedor de dependencias (o inyección manual en routers)

## 2. Migración 006 e integridad append-only

- [x] 2.1 Crear migración `006_audit_log.py` con: creación de tabla `audit_log`, trigger function y trigger BEFORE UPDATE/DELETE, seed del permiso `impersonacion:usar` (modulo: `auth`), seed en `rol_permiso` para ADMIN y COORDINADOR
- [x] 2.2 Implementar downgrade: dropear trigger, dropear función, dropear tabla, limpiar seed data
- [x] 2.3 Documentar en `CHANGES.md` y `docs/` la existencia del trigger y su propósito (defensa en profundidad)

## 3. Impersonación (endpoints y lógica)

- [x] 3.1 Crear `app/services/impersonation.py` con lógica: verificar permiso `impersonacion:usar`, crear JWT con flag `impersonating: true`, mantener `actor_id` original en claims
- [x] 3.2 Crear endpoint `POST /auth/impersonate/{user_id}` que inicia impersonación: valida permiso, verifica usuario target existe, genera JWT de impersonación, registra `IMPERSONACION_INICIAR` en audit log
- [x] 3.3 Crear endpoint `POST /auth/impersonate/stop` que finaliza impersonación: verifica que hay impersonación activa, regenera JWT original, registra `IMPERSONACION_FINALIZAR` en audit log
- [x] 3.4 Actualizar `get_current_user` en `core/dependencies.py` para detectar el flag `impersonating` y exponer `request.state.actor_id`

## 4. Endpoint de consulta de audit log

- [x] 4.1 Crear router `GET /audit-log` con filtros: accion, actor_id, fecha_desde, fecha_hasta, paginación (limit/offset)
- [x] 4.2 Proteger endpoint con `require_permission("auditoria:ver")`
- [x] 4.3 Crear Pydantic schema de respuesta con los campos del audit log

## 5. Tests

- [x] 5.1 Test: crear registro de auditoría via AuditService (assert campos correctos)
- [x] 5.2 Test: append-only a nivel repositorio (assert que no hay métodos update/delete)
- [x] 5.3 Test: trigger bloquea UPDATE directo en DB
- [x] 5.4 Test: trigger bloquea DELETE directo en DB
- [x] 5.5 Test: inicio de impersonación exitoso (assert audit log `IMPERSONACION_INICIAR`)
- [x] 5.6 Test: finalización de impersonación exitosa (assert audit log `IMPERSONACION_FINALIZAR`)
- [x] 5.7 Test: acción bajo impersonación registra actor_id real + impersonado_id
- [x] 5.8 Test: acción sin impersonación registra actor_id y impersonado_id = NULL
- [x] 5.9 Test: endpoint GET /audit-log con filtros devuelve resultados correctos
- [x] 5.10 Test: endpoint GET /audit-log sin permiso auditoria:ver devuelve 403
- [x] 5.11 Test: endpoint POST /auth/impersonate/{id} sin permiso devuelve 403
- [x] 5.12 Test: endpoint POST /auth/impersonate/{id} sobre usuario inexistente devuelve 404
- [x] 5.13 Test: endpoint POST /auth/impersonate/stop sin impersonación activa devuelve 400
