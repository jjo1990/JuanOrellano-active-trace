## ADDED Requirements

### Requirement: Cross-sectional monitor for COORD/ADMIN

The system SHALL provide an endpoint `GET /api/analisis/monitor` that returns a cross-sectional view of all students across the tenant with their activity status.

The endpoint SHALL accept optional query parameters:
- `materia_id`: UUID — filter by specific materia
- `regional`: str — filter by regional
- `comision`: str — filter by comision
- `alumno`: str — free-text search on student name or email
- `estado`: str — filter by state: "atrasado", "al_dia", "aprobado_todos"

The system SHALL compute for each student their consolidated status and return a paginatable list.

The response SHALL include per student: EntradaPadron data, materia info, estado (atrasado/al_dia/aprobado_todos), total_actividades, aprobadas, faltantes, ultima_actividad_date.

#### Scenario: Filter by materia

- **WHEN** monitor is called with `materia_id=X`
- **THEN** only students in materia X are returned

#### Scenario: Filter by regional

- **WHEN** monitor is called with `regional="Centro"`
- **THEN** only students with regional "Centro" are returned

#### Scenario: Filter by estado atrasado

- **WHEN** monitor is called with `estado="atrasado"`
- **THEN** only students currently atrasados are returned

#### Scenario: Free-text search by name

- **WHEN** monitor is called with `alumno="García"`
- **THEN** only students whose nombre or apellidos contain "García" (case-insensitive) are returned

#### Scenario: Combined filters

- **WHEN** monitor is called with `materia_id=X`, `regional="Norte"`, `estado="atrasado"`
- **THEN** only atrasados in materia X with regional "Norte" are returned

#### Scenario: No filters returns all students

- **WHEN** monitor is called without any query params
- **THEN** all students across the tenant are returned

#### Scenario: Monitor response schema

- **WHEN** the monitor is computed
- **THEN** the response SHALL contain `total`, `estudiantes: list[MonitorEntryDTO]` with fields `entrada_padron_id`, `nombre`, `apellidos`, `email`, `materia_id`, `materia_nombre`, `comision`, `regional`, `estado`, `total_actividades`, `aprobadas`, `faltantes`, `ultima_actividad`

#### Scenario: Tenant isolation

- **WHEN** tenant A requests the monitor
- **THEN** only tenant A's students are returned
