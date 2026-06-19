## ADDED Requirements

### Requirement: Asignar múltiples docentes en bloque
The system SHALL allow COORDINADOR and ADMIN to create asignaciones for multiple users in a single request against a common academic context (materia × carrera × cohorte × rol × vigencia).

#### Scenario: Asignación masiva exitosa con múltiples docentes
- **WHEN** COORDINADOR envía `POST /api/equipos/asignacion-masiva` con `{usuarios: [{id: uuid1}, {id: uuid2}], materia_id: uuid, carrera_id: uuid, cohorte_id: uuid, rol_id: uuid, comisiones: ["A", "B"], desde: "2026-08-01", hasta: "2026-12-31"}`
- **THEN** system returns 201 con `{asignaciones_creadas: [asignacion1, asignacion2], errores: [], total_procesados: 2, total_exitosos: 2, total_fallidos: 0}`
- **AND** ambas asignaciones quedan persistidas con los mismos `materia_id`, `carrera_id`, `cohorte_id`, `rol_id`, `comisiones`, `desde`, `hasta`

#### Scenario: Asignación masiva con algunos fallos individuales
- **WHEN** COORDINADOR envía `POST /api/equipos/asignacion-masiva` con usuarios donde uno tiene `usuario_id` inexistente
- **THEN** system returns 201 con `total_exitosos` > 0 y `errores` conteniendo `[{usuario_id: uuid, error: "Usuario no encontrado"}]`
- **AND** las asignaciones válidas se crean, las inválidas se reportan sin detener el proceso

#### Scenario: Sin permiso equipos:asignar
- **WHEN** un usuario sin permiso `equipos:asignar` envía `POST /api/equipos/asignacion-masiva`
- **THEN** system returns 403 Forbidden

#### Scenario: Fechas inválidas en asignación masiva
- **WHEN** COORDINADOR envía `POST /api/equipos/asignacion-masiva` con `desde > hasta`
- **THEN** system returns 400 Bad Request con mensaje indicando que `hasta` debe ser posterior o igual a `desde`

#### Scenario: Asignación masiva sin usuarios
- **WHEN** COORDINADOR envía `POST /api/equipos/asignacion-masiva` con `usuarios: []`
- **THEN** system returns 400 Bad Request indicando que se requiere al menos un usuario

#### Scenario: Rollback parcial no aplica — operación best-effort
- **WHEN** una asignación masiva falla para algunos usuarios pero no para otros
- **THEN** las asignaciones exitosas quedan persistidas (no hay rollback automático porque cada asignación es independiente)

### Requirement: Búsqueda de usuarios con autocompletado (RN-30)
The system SHALL provide server-assisted autocomplete search to locate users for the bulk assignment UI.

#### Scenario: Búsqueda por nombre parcial
- **WHEN** COORDINADOR envía `GET /api/equipos/buscar-usuarios?q=mar&incluir_roles=PROFESOR,TUTOR`
- **THEN** system returns 200 con lista de usuarios cuyo nombre o apellido contiene "mar" (case-insensitive) y que tienen al menos un rol en la lista de inclusión
- **AND** cada resultado incluye `id`, `nombre`, `apellido`, `email`, `legajo`

#### Scenario: Búsqueda sin query
- **WHEN** COORDINADOR envía `GET /api/equipos/buscar-usuarios?q=`
- **THEN** system returns 200 con lista vacía (no se devuelven todos los usuarios)

#### Scenario: Búsqueda limitada al tenant
- **WHEN** COORDINADOR del tenant A busca usuarios
- **THEN** system returns 200 con solo usuarios del tenant A
