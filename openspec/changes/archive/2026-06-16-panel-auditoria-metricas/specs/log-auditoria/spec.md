## ADDED Requirements

### Requirement: Log completo de auditoría con filtros
El sistema SHALL exponer el registro completo de auditoría con filtros avanzados (F9.2, HU-38).

#### Scenario: ADMIN consulta log completo
- **WHEN** un ADMIN envía `GET /api/auditoria/log`
- **THEN** devuelve registros de AuditLog con campos: fecha_hora, actor_id, materia_id, accion, filas_afectadas, ip, user_agent. Ordenado por fecha_hora DESC.

#### Scenario: Filtrar log por usuario
- **WHEN** `GET /api/auditoria/log?usuario_id=X`
- **THEN** solo devuelve acciones de ese usuario

#### Scenario: Filtrar log por acción
- **WHEN** `GET /api/auditoria/log?accion=CALIFICACIONES_IMPORTAR`
- **THEN** solo devuelve registros con ese código de acción

#### Scenario: Filtrar log por materia
- **WHEN** `GET /api/auditoria/log?materia_id=X`
- **THEN** solo devuelve acciones sobre esa materia

#### Scenario: COORDINADOR con scope propio
- **WHEN** un COORDINADOR consulta el log
- **THEN** solo ve acciones de materias donde tiene asignación

#### Scenario: Paginación
- **WHEN** `GET /api/auditoria/log?limite=50&offset=100`
- **THEN** devuelve máximo 50 registros saltando los primeros 100

### Requirement: Registro inmutable
El sistema SHALL garantizar que los registros de auditoría son de solo lectura (RN-23).

#### Scenario: Intentar modificar registro
- **WHEN** cualquier request intenta modificar un AuditLog
- **THEN** el endpoint no existe (no hay PUT/PATCH/DELETE en /api/auditoria/log)
