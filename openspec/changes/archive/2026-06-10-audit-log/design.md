## Context

C-04 (RBAC) estableció roles, permisos finos, `rol_permiso`, `usuario_rol` y el guard `require_permission`. Sobre esa base, C-05 implementa el **log de auditoría append-only** (principio "todo audita") y la **impersonación** (suplantación legítima para diagnóstico). El modelo de datos está definido en la KB como E-AUD. Los códigos de acción están estandarizados. La impersonación requiere permiso `impersonacion:usar` (no seedeado en C-04).

**Estado actual:**
- Tablas RBAC creadas (rol, permiso, rol_permiso, usuario_rol)
- Permisos seedeados: 20 permisos, matriz completa (sin `impersonacion:usar`)
- No existe tabla `audit_log`
- No existe mecanismo de audit helper
- No existe lógica de impersonación

## Goals / Non-Goals

**Goals:**
- Modelo `AuditLog` con campos exactos de E-AUD (id, tenant_id, fecha_hora, actor_id, impersonado_id nullable, materia_id nullable, accion, detalle JSON, filas_afectadas, ip, user_agent)
- Append-only enforcement en dos capas: repositorio (solo create/list) + trigger PostgreSQL BEFORE UPDATE/DELETE
- `AuditService.log()` como función utilitaria para services
- Endpoints de impersonación: iniciar (`POST /auth/impersonate/{user_id}`) y finalizar (`POST /auth/impersonate/stop`)
- Permiso `impersonacion:usar` en seed + asignado a ADMIN
- Migración 006 con tabla, seed y trigger
- Cobertura de tests: append-only, atribución bajo impersonación, registro con código + filas afectadas

**Non-Goals:**
- UI de auditoría (frontend) — será en cambio posterior
- Catálogo administrable de códigos de acción (constantes hardcodeadas, YAGNI)
- Vigencia temporal en impersonación (sesión explícita, no vencimiento automático)
- Rate limiting por consulta de auditoría

## Decisions

### D1: Append-only enforcement en dos capas (repositorio + trigger DB)

- **Opción A (elegida)**: Repository `AuditLogRepository` que solo expone `create()` y `list()` (sin update/delete), más un trigger `BEFORE UPDATE OR DELETE` en la tabla `audit_log` que lanza excepción.
- **Opción B**: Solo repositorio sin update/delete.
- **Por qué A**: Defensa en profundidad. El trigger protege contra accesos directos a DB, errores en migraciones, o bugs en el repositorio. La capa app es la primera barrera; el trigger es la segunda. Sin trigger, un error de código podría romper la inmutabilidad.

### D2: AuditService como servicio con método `log()`

- **Opción A (elegida)**: `AuditService.log(actor_id, tenant_id, accion, detalle=None, filas_afectadas=0, request=None, impersonado_id=None)` que recibe parámetros explícitos y escribe via `AuditLogRepository`.
- **Opción B**: Decorador `@audit(accion="...")` en métodos de service.
- **Por qué A**: El decorador necesitaría inspeccionar argumentos del método para extraer actor/tenant/request, lo que lo vuelve frágil y difícil de testear. Un método explícito es comprobable, predecible y no oculta dependencias.

### D3: Impersonación como flag en request context (sin DB)

- **Opción A (elegida)**: La impersonación se almacena como un flag en el request context (via `request.state.impersonating`). Endpoints `POST /auth/impersonate/{user_id}` y `POST /auth/impersonate/stop`. Cada acción bajo impersonación registra `impersonado_id` en el audit log.
- **Opción B**: Tabla `impersonacion_activa` en DB con FK y flag activo.
- **Por qué A**: La impersonación es un estado de sesión, no un dato persistente. Si el usuario cierra sesión, la impersonación termina. No hay necesidad de persistencia cross-session. YAGNI.

### D4: Códigos de acción como constantes Python

- **Opción A (elegida)**: Módulo `app/core/action_codes.py` con constantes tipo `CALIFICACIONES_IMPORTAR = "CALIFICACIONES_IMPORTAR"`.
- **Opción B**: Tabla `codigo_accion` en DB.
- **Por qué A**: Los códigos son fijos y estandarizados por la KB. No se administran dinámicamente. Una tabla agregaría complejidad sin beneficio actual.

### D5: `impersonacion:usar` asignado a ADMIN (y opcionalmente COORDINADOR)

- **Opción A (elegida)**: Se agrega `impersonacion:usar` a la matriz de ADMIN. También a COORDINADOR para permitir impersonación a nivel supervisión.
- **Opción B**: Solo ADMIN.
- **Por qué A**: La KB §3.5 dice "usuario autorizado (soporte, ADMIN)". COORDINADOR puede necesitar impersonar para diagnóstico en sus materias. El permiso granular permite que el tenant decida quién lo tiene.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| **R1**: El trigger BEFORE UPDATE/DELETE puede interferir con migraciones futuras que necesiten modificar la tabla | El trigger se dropea al inicio de la migración que modifica audit_log y se recrea al final. Documentado en el playbook de migraciones. |
| **R2**: AuditService accesible desde cualquier service sin restricción — podría usarse incorrectamente | Se documenta como singleton inyectado. No hay restricción técnica porque cualquier service puede necesitar auditar. |
| **R3**: Impersonación en request context se pierde si hay múltiples workers | En una app WSGI/ASGI típica, las requests son single-thread y no comparten estado. Si se escala a múltiples workers, cada request mantiene su propio context. No hay fuga de impersonación entre requests. |
| **R4**: El seed de `impersonacion:usar` no se aplica retroactivamente a tenants existentes | La migración 006 inserta el permiso y las filas en `rol_permiso` para ADMIN y COORDINADOR. Los tenants existentes lo obtienen automáticamente al migrar. |

## Migration Plan

### Forward (006_audit_log.py)
1. Crear tabla `audit_log` con todos los campos E-AUD + soft delete (por consistencia, aunque nunca se usará)
2. Crear trigger `trg_audit_log_append_only` (BEFORE UPDATE OR DELETE → RAISE EXCEPTION)
3. Insertar permiso `impersonacion:usar` en `permiso` (módulo `auth`)
4. Insertar filas en `rol_permiso` para ADMIN y COORDINADOR con ese permiso

### Rollback (downgrade)
1. Dropear trigger `trg_audit_log_append_only`
2. Dropear tabla `audit_log`
3. Eliminar filas de `rol_permiso` para `impersonacion:usar`
4. Eliminar permiso `impersonacion:usar` (si no hay otras referencias)

### Estructura de migración propuesta

```python
def upgrade():
    op.create_table("audit_log", ...)
    op.execute("CREATE OR REPLACE FUNCTION fn_audit_log_append_only() RETURNS TRIGGER AS $$ ... $$ LANGUAGE plpgsql;")
    op.execute("CREATE TRIGGER trg_audit_log_append_only BEFORE UPDATE OR DELETE ON audit_log ...;")
    # Seed: permiso + matriz
    # (similar al patrón de 005_rbac.py)

def downgrade():
    op.execute("DROP TRIGGER IF EXISTS trg_audit_log_append_only ON audit_log;")
    op.execute("DROP FUNCTION IF EXISTS fn_audit_log_append_only();")
    op.drop_table("audit_log")
    # Remove seed data
```

## Open Questions

- **OQ1**: ¿El modelo `AuditLog` hereda de `BaseModelMixin` (con soft-delete) aunque nunca se use? Decisión: sí, por consistencia con todos los demás modelos. El trigger impide que `deleted_at` se modifique.
- **OQ2**: ¿Se expone un endpoint GET para consultar el audit log? Decisión: sí, `GET /audit-log` con filtros por accion, actor_id, fecha_desde, fecha_hasta, paginado. Protegido con `auditoria:ver`.
- **OQ3**: ¿Se validan los códigos de acción en el AuditLog o se almacenan como string libre? Decisión: se almacenan como string libre (la validación la hace el AuditService con las constantes). La DB no tiene FK ni enum para flexibilidad.
