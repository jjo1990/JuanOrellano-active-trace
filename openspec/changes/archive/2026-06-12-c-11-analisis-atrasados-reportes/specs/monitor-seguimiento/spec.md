## ADDED Requirements

### Requirement: Teacher-specific follow-up monitor

The system SHALL provide an endpoint `GET /api/analisis/monitor/seguimiento` that returns the activity status of students assigned to the authenticated teacher.

The endpoint SHALL filter results to the authenticated user's asignaciones (only students in materias where the user has an active Asignacion).

The endpoint SHALL accept optional query parameters:
- `alumno`: str — free-text search on student name or email
- `comision`: str — filter by comision
- `regional`: str — filter by regional
- `actividad`: str — filter by specific activity name
- `min_aprobadas`: int — minimum number of approved activities

The response SHALL include per student their status relative to the teacher's assigned materias.

#### Scenario: Teacher sees only their own students

- **WHEN** teacher T (with asignacion to materia X only) requests seguimiento
- **THEN** only students in materia X are returned; students from materia Y (where T has no asignacion) are excluded

#### Scenario: Filter by min approved activities

- **WHEN** seguimiento is called with `min_aprobadas=3`
- **THEN** only students with >=3 approved activities are returned

#### Scenario: Filter by activity name

- **WHEN** seguimiento is called with `actividad="TP1"`
- **THEN** results reflect only status for activity "TP1"

#### Scenario: Combined filters

- **WHEN** seguimiento is called with `comision="A"`, `regional="Sur"`, `min_aprobadas=2`
- **THEN** only students in comision "A" with regional "Sur" and >=2 approved activities are returned

#### Scenario: Seguimiento response schema

- **WHEN** the seguimiento is computed
- **THEN** the response SHALL contain `total`, `estudiantes: list[SeguimientoEntryDTO]` with fields `entrada_padron_id`, `nombre`, `apellidos`, `email`, `materia_id`, `materia_nombre`, `comision`, `regional`, `estado`, `total_actividades`, `aprobadas`, `faltantes`

#### Scenario: Tenant isolation

- **WHEN** a teacher in tenant A requests seguimiento
- **THEN** only tenant A's data is returned
