## ADDED Requirements

### Requirement: Grouped final grades per student

The system SHALL provide an endpoint `GET /api/analisis/notas-finales/{materia_id}` that groups calificaciones by student and returns a consolidated view suitable for actas or end-of-period reports.

For each student, the system SHALL compute:
- `nota_final`: average of all `nota_numerica` values for that student (ignoring textual-only calificaciones)
- `aprobado_final`: boolean indicating whether `nota_final >= umbral_pct` (or all textual notas are in valores_aprobatorios if only textual exist)
- List of all calificaciones with their individual aprobado status

If a student has only textual calificaciones, `nota_final` SHALL be None and `aprobado_final` SHALL be True only if ALL textual calificaciones have notas in valores_aprobatorios.

#### Scenario: Student with mixed numeric and textual

- **WHEN** student S has nota_numerica=70, nota_numerica=80, and nota_textual="Satisfactorio" for 3 activities
- **THEN** nota_final = 75.0 (average of 70 and 80), aprobado_final = True (75 >= 60 default)

#### Scenario: Student with only textual calificaciones

- **WHEN** student S has nota_textual="Satisfactorio" and nota_textual="Supera lo esperado"
- **THEN** nota_final = None, aprobado_final = True

#### Scenario: Student with only textual and one not approved

- **WHEN** student S has nota_textual="Satisfactorio" and nota_textual="Regular"
- **THEN** nota_final = None, aprobado_final = False

#### Scenario: Student with nota_final below umbral

- **WHEN** student S has nota_numerica=50 and nota_numerica=55, umbral_pct=60
- **THEN** nota_final = 52.5, aprobado_final = False

#### Scenario: No calificaciones for materia

- **WHEN** materia X has zero calificaciones
- **THEN** the endpoint returns an empty list with status_info

#### Scenario: Notas finales response schema

- **WHEN** the grouped grades are computed
- **THEN** the response SHALL contain `materia_id`, `notas: list[NotaFinalDTO]` with fields `entrada_padron_id`, `nombre`, `apellidos`, `email`, `comision`, `regional`, `nota_final` (float|null), `aprobado_final` (bool), `calificaciones: list[CalificacionDTO]`

#### Scenario: Tenant isolation

- **WHEN** tenant A requests notas finales
- **THEN** only tenant A's calificaciones are aggregated
