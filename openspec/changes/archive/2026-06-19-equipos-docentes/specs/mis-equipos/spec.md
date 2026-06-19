## ADDED Requirements

### Requirement: El usuario autenticado SHALL ver sus propias asignaciones con datos enriquecidos
The system SHALL provide an endpoint `GET /api/equipos/mis-equipos` that returns all asignaciones of the authenticated user, enriched with names from related entities (user, rol, materia, carrera, cohorte) instead of raw UUIDs.

#### Scenario: Docente ve sus equipos con datos completos
- **WHEN** un PROFESOR autenticado envía `GET /api/equipos/mis-equipos`
- **THEN** system returns 200 con una lista de objetos que incluyen `usuario_nombre`, `usuario_apellido`, `rol_nombre`, `materia_nombre`, `carrera_nombre`, `cohorte_nombre`, `comisiones`, `desde`, `hasta`, `estado_vigencia` (derivado: "Vigente" o "Vencida")
- **AND** solo se devuelven asignaciones del tenant del usuario autenticado
- **AND** solo se devuelven asignaciones no eliminadas (soft delete)

#### Scenario: Usuario sin asignaciones
- **WHEN** un usuario autenticado sin asignaciones envía `GET /api/equipos/mis-equipos`
- **THEN** system returns 200 con lista vacía

#### Scenario: Usuario no autenticado
- **WHEN** se envía `GET /api/equipos/mis-equipos` sin token JWT
- **THEN** system returns 401 Unauthorized

### Requirement: Filtrar mis equipos por criterios
The system SHALL support filtering the authenticated user's asignaciones by estado, materia, rol, carrera, and cohorte.

#### Scenario: Filtrar solo asignaciones vigentes
- **WHEN** PROFESOR envía `GET /api/equipos/mis-equipos?vigente=true`
- **THEN** system returns 200 con solo las asignaciones donde `desde <= today AND (hasta IS NULL OR hasta >= today)`

#### Scenario: Filtrar por materia
- **WHEN** PROFESOR envía `GET /api/equipos/mis-equipos?materia_id={uuid}`
- **THEN** system returns 200 con solo las asignaciones de esa materia

#### Scenario: Filtrar por rol
- **WHEN** PROFESOR envía `GET /api/equipos/mis-equipos?rol_id={uuid}`
- **THEN** system returns 200 con solo las asignaciones donde el usuario tiene ese rol

#### Scenario: Combinación de filtros
- **WHEN** PROFESOR envía `GET /api/equipos/mis-equipos?vigente=true&materia_id={uuid}&rol_id={uuid}`
- **THEN** system returns 200 con asignaciones que cumplen todos los filtros simultáneamente

### Requirement: Aislamiento multi-tenant en mis equipos
The system SHALL never expose asignaciones de otros tenants en la vista mis-equipos.

#### Scenario: Usuario solo ve datos de su tenant
- **WHEN** un usuario del tenant A envía `GET /api/equipos/mis-equipos`
- **THEN** system returns 200 con solo asignaciones donde `tenant_id` coincide con el del token JWT
