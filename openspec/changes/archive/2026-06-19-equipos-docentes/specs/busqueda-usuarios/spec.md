## ADDED Requirements

### Requirement: Autocompletado de usuarios para asignación masiva (RN-30)
The system SHALL provide a server-assisted autocomplete endpoint to search users by name, surname, or legacy ID for the bulk assignment workflow.

#### Scenario: Búsqueda por nombre parcial
- **WHEN** COORDINADOR envía `GET /api/equipos/buscar-usuarios?q=gonzalez&limite=20`
- **THEN** system returns 200 con hasta 20 usuarios cuyo `nombre` o `apellido` contiene "gonzalez" (case-insensitive)
- **AND** cada resultado incluye `{id, nombre, apellido, email, legajo}`

#### Scenario: Búsqueda por legajo
- **WHEN** COORDINADOR envía `GET /api/equipos/buscar-usuarios?q=LEG-1234`
- **THEN** system returns 200 con usuarios cuyo `legajo` coincide (case-insensitive LIKE)

#### Scenario: Búsqueda con filtro de roles
- **WHEN** COORDINADOR envía `GET /api/equipos/buscar-usuarios?q=mar&roles=PROFESOR,TUTOR`
- **THEN** system returns 200 con solo usuarios que tienen al menos un `UsuarioRol` o `Asignacion` vigente con rol PROFESOR o TUTOR

#### Scenario: Búsqueda sin resultados
- **WHEN** COORDINADOR envía `GET /api/equipos/buscar-usuarios?q=xyz123`
- **THEN** system returns 200 con lista vacía

#### Scenario: Búsqueda sin query
- **WHEN** COORDINADOR envía `GET /api/equipos/buscar-usuarios?q=`
- **THEN** system returns 200 con lista vacía (no se permite listar todos los usuarios)

#### Scenario: Aislamiento multi-tenant
- **WHEN** COORDINADOR del tenant A busca usuarios
- **THEN** system returns 200 con solo usuarios del tenant A

#### Scenario: Límite de resultados
- **WHEN** COORDINADOR envía `GET /api/equipos/buscar-usuarios?q=a&limite=5`
- **THEN** system returns 200 con máximo 5 resultados
