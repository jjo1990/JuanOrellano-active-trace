## ADDED Requirements

### Requirement: Crear asignación
The system SHALL allow users with `equipos:asignar` permission to create asignaciones linking a user to a role within academic context.

#### Scenario: Creación con contexto completo
- **WHEN** COORDINADOR envía POST `/api/asignaciones` con `{usuario_id, rol_id, materia_id, carrera_id, cohorte_id, comisiones: ["A", "B"], responsable_id, desde: "2026-03-01", hasta: "2026-12-31"}`
- **THEN** system returns 201 con la asignación creada
- **AND** `comisiones` se almacena como JSONB

#### Scenario: Creación sin materia (rol global)
- **WHEN** COORDINADOR envía POST `/api/asignaciones` con `{usuario_id, rol_id, carrera_id, cohorte_id, desde: "2026-03-01"}` sin `materia_id`
- **THEN** system returns 201
- **AND** `materia_id` es NULL (rol sin contexto de materia, ej: ADMIN, FINANZAS)

#### Scenario: Creación sin fecha fin (abierta)
- **WHEN** COORDINADOR envía POST `/api/asignaciones` con `{usuario_id, rol_id, materia_id, desde: "2026-03-01"}` sin `hasta`
- **THEN** system returns 201
- **AND** `hasta` es NULL (asignación abierta)

#### Scenario: Sin permiso equipos:asignar
- **WHEN** usuario sin permiso `equipos:asignar` intenta crear una asignación
- **THEN** system returns 403 Forbidden

#### Scenario: Referencia a usuario inexistente
- **WHEN** se crea asignación con `usuario_id` que no existe
- **THEN** system returns 404 o 409 indicando violación de FK

#### Scenario: Referencia a rol inexistente
- **WHEN** se crea asignación con `rol_id` que no existe
- **THEN** system returns 404 o 409 indicando violación de FK

### Requirement: Listar asignaciones
The system SHALL allow users with `equipos:asignar` to list asignaciones with filters.

#### Scenario: Listado con filtros
- **WHEN** COORDINADOR envía GET `/api/asignaciones?materia_id={id}&rol_id={id}`
- **THEN** system returns 200 con asignaciones filtradas

#### Scenario: Filtro por vigencia activa
- **WHEN** COORDINADOR envía GET `/api/asignaciones?vigente=true`
- **THEN** system returns 200 con solo asignaciones donde `desde <= today AND (hasta IS NULL OR hasta >= today)`

#### Scenario: Filtro por usuario
- **WHEN** COORDINADOR envía GET `/api/asignaciones?usuario_id={id}`
- **THEN** system returns 200 con todas las asignaciones de ese usuario (vigentes y vencidas)

#### Scenario: Aislamiento multi-tenant
- **WHEN** COORDINADOR del tenant A lista asignaciones
- **THEN** system returns 200 con solo asignaciones del tenant A

### Requirement: Obtener asignación por ID
The system SHALL allow retrieving a single asignación by UUID.

#### Scenario: Asignación existe
- **WHEN** COORDINADOR envía GET `/api/asignaciones/{id}`
- **THEN** system returns 200 con datos completos de la asignación

#### Scenario: Asignación no existe
- **WHEN** COORDINADOR envía GET `/api/asignaciones/{id}` con UUID inexistente
- **THEN** system returns 404 Not Found

### Requirement: Actualizar asignación
The system SHALL allow updating asignación fields.

#### Scenario: Modificar vigencia
- **WHEN** COORDINADOR envía PUT `/api/asignaciones/{id}` con `{desde: "2026-04-01", hasta: "2026-12-31"}`
- **THEN** system returns 200 con la asignación actualizada

#### Scenario: Modificar responsable
- **WHEN** COORDINADOR envía PUT `/api/asignaciones/{id}` con `{responsable_id: {otro-id}}`
- **THEN** system returns 200
- **AND** el responsable queda actualizado

#### Scenario: Modificar comisiones
- **WHEN** COORDINADOR envía PUT `/api/asignaciones/{id}` con `{comisiones: ["A", "C"]}`
- **THEN** system returns 200
- **AND** comisiones se actualiza en JSONB

### Requirement: Eliminar asignación (soft delete)
The system SHALL perform soft delete on asignaciones.

#### Scenario: Soft delete
- **WHEN** COORDINADOR envía DELETE `/api/asignaciones/{id}`
- **THEN** system returns 204
- **AND** `deleted_at` se setea (no se borra físicamente)

#### Scenario: Soft delete de asignación ya eliminada
- **WHEN** COORDINADOR envía DELETE sobre asignación ya eliminada
- **THEN** system returns 404 Not Found

### Requirement: Asignación vencida no otorga permisos
The system SHALL NOT grant permissions through expired asignaciones.

#### Scenario: Verificación de vigencia en autorización
- **WHEN** un usuario tiene solo asignaciones con `hasta < today`
- **THEN** system deniega acceso a recursos protegidos por esas asignaciones
- **AND** las asignaciones se conservan en DB (histórico)

#### Scenario: Asignación vigente sí autoriza
- **WHEN** un usuario tiene asignación con `desde <= today AND (hasta IS NULL OR hasta >= today)`
- **THEN** system otorga los permisos del rol vinculado

### Requirement: Jerarquía docente (responsable_id)
The system SHALL support hierarchy via `responsable_id` in asignaciones.

#### Scenario: Asignación con responsable
- **WHEN** COORDINADOR crea asignación para TUTOR con `responsable_id` apuntando a un PROFESOR
- **THEN** system permite consultar "¿quién supervisa a este usuario?" vía el responsable de cualquiera de sus asignaciones

#### Scenario: Auto-referencia no válida
- **WHEN** COORDINADOR intenta setear `responsable_id = usuario_id` (misma persona)
- **THEN** system NO valida esta regla a nivel DB (pero service puede advertir)
