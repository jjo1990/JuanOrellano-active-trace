## ADDED Requirements

### Requirement: AuditLog con modelo E-AUD
El sistema SHALL tener un modelo `AuditLog` con los siguientes campos: `id` (UUID PK), `tenant_id` (FK → Tenant), `fecha_hora` (TIMESTAMP with timezone), `actor_id` (FK → User), `impersonado_id` (FK → User, nullable), `materia_id` (FK → Materia, nullable), `accion` (VARCHAR 100), `detalle` (JSONB, nullable), `filas_afectadas` (INTEGER, default 0), `ip` (VARCHAR 45, nullable), `user_agent` (VARCHAR 500, nullable). El modelo SHALL heredar de `BaseModelMixin`.

#### Scenario: Crear registro de auditoría
- **WHEN** un service llama a `AuditService.log()` con actor_id, tenant_id, accion y opcionales
- **THEN** el sistema crea un registro en `audit_log` con los datos provistos y `fecha_hora = now()`

#### Scenario: Registro con detalle JSON
- **WHEN** un service provee un dict en el parámetro `detalle`
- **THEN** el registro almacena el dict como JSONB en la columna `detalle`

### Requirement: Append-only enforcement
El sistema SHALL garantizar que ningún registro de `audit_log` pueda ser modificado ni eliminado, ni a nivel de aplicación ni a nivel de base de datos.

#### Scenario: Repositorio sin update/delete
- **WHEN** un service intenta llamar a `update()` o `delete()` en `AuditLogRepository`
- **THEN** el repositorio NO expone esos métodos (solo `create()` y `list()`)

#### Scenario: Trigger bloquea UPDATE directo
- **WHEN** alguien ejecuta `UPDATE audit_log SET ...` directamente en la base de datos
- **THEN** el trigger `trg_audit_log_append_only` lanza una excepción y la operación es rechazada

#### Scenario: Trigger bloquea DELETE directo
- **WHEN** alguien ejecuta `DELETE FROM audit_log` directamente en la base de datos
- **THEN** el trigger `trg_audit_log_append_only` lanza una excepción y la operación es rechazada

### Requirement: AuditService con códigos estandarizados
El sistema SHALL proveer un `AuditService` con un método `log()` que acepte `actor_id`, `tenant_id`, `accion` (string), y opcionalmente `detalle` (dict), `filas_afectadas` (int), `request` (para extraer IP y user-agent), `impersonado_id` (UUID nullable). Los códigos de acción SHALL estar definidos como constantes en `app/core/action_codes.py`.

#### Scenario: AuditService registra acción con IP y user-agent
- **WHEN** un service llama a `AuditService.log()` con un objeto `request` que tiene IP y user-agent
- **THEN** el registro incluye la IP del cliente y el user-agent extraídos del request

#### Scenario: AuditService registra acción sin request
- **WHEN** un service llama a `AuditService.log()` sin proveer `request`
- **THEN** el registro tiene `ip = None` y `user_agent = None`

#### Scenario: AuditService usa constantes de action_codes
- **WHEN** un service pasa `action_codes.CALIFICACIONES_IMPORTAR` como `accion`
- **THEN** el registro almacena el string `"CALIFICACIONES_IMPORTAR"` en la columna `accion`

### Requirement: Registro con filas afectadas
El sistema SHALL permitir registrar la cantidad de filas afectadas por una acción.

#### Scenario: Importación masiva con filas afectadas
- **WHEN** un service importa 150 calificaciones y llama a `AuditService.log(filas_afectadas=150, ...)`
- **THEN** el registro de auditoría almacena `filas_afectadas = 150`

### Requirement: Consulta de audit log
El sistema SHALL exponer un endpoint `GET /audit-log` que permita listar registros de auditoría con filtros por `accion`, `actor_id`, `fecha_desde`, `fecha_hasta`, y paginación. El endpoint SHALL requerir el permiso `auditoria:ver`.

#### Scenario: Listar registros con filtro por acción
- **WHEN** un usuario con permiso `auditoria:ver` consulta `GET /audit-log?accion=CALIFICACIONES_IMPORTAR`
- **THEN** el sistema devuelve solo los registros con esa acción, paginados

#### Scenario: Sin permiso devuelve 403
- **WHEN** un usuario SIN permiso `auditoria:ver` consulta `GET /audit-log`
- **THEN** el sistema devuelve HTTP 403 Forbidden
