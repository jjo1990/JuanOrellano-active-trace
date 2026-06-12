## ADDED Requirements

### Requirement: Quick reports per materia

The system SHALL provide an endpoint `GET /api/analisis/reportes/{materia_id}` that returns consolidated key metrics for a materia.

The response SHALL include:
- `total_alumnos`: number of students in the active padrón
- `total_actividades`: number of distinct activities with calificaciones
- `aprobacion_general`: percentage of all calificaciones that are approved
- `distribucion_notas`: count per nota range (e.g., 0-59, 60-69, 70-79, 80-89, 90-100)
- `alumnos_al_dia`: count of students NOT atrasados
- `alumnos_atrasados`: count of atrasados
- `actividad_mas_dificil`: activity name with lowest approval rate
- `actividad_mas_facil`: activity name with highest approval rate

When there are no calificaciones for the materia, the system SHALL return a status_info message indicating the absence of data and all metrics SHALL be 0 or empty.

#### Scenario: Materia with complete data

- **WHEN** materia X has 50 students and 5 activities with varied calificaciones
- **THEN** the response contains all metrics computed from the data

#### Scenario: Materia with no calificaciones

- **WHEN** materia X has padrón but zero calificaciones
- **THEN** total_actividades=0, all metrics are 0, and status_info indicates missing data

#### Scenario: Multiple activities found

- **WHEN** materia X has calificaciones for 3 distinct activities
- **THEN** total_actividades=3 and distribucion_notas covers all calificaciones

#### Scenario: Reportes response schema

- **WHEN** the report is computed
- **THEN** the response SHALL conform to the schema with all fields present and `extra='forbid'`

#### Scenario: Tenant isolation

- **WHEN** tenant A requests reportes and tenant B has data for the same materia
- **THEN** only tenant A's data is aggregated
