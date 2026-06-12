## ADDED Requirements

### Requirement: Compute atrasados for materia

The system SHALL provide an endpoint `GET /api/analisis/atrasados/{materia_id}` that returns a list of students considered "atrasados" according to RN-06.

A student is atrasado when EITHER:
- They have missing activities (actividades faltantes) — activities present in the materia's universe but without a calificacion for that student.
- They have at least one calificacion with nota below the configured umbral (nota_numerica < umbral_pct for numeric, or nota_textual NOT IN valores_aprobatorios for textual).

The response SHALL include per student: their EntradaPadron data (nombre, apellidos, email, comision, regional) plus detalle of which activities are missing and which have nota baja.

The system SHALL apply tenant isolation: only calificaciones and entradas belonging to the authenticated user's tenant are considered.

The system SHALL use default umbral (umbral_pct=60, valores_aprobatorios=["Satisfactorio", "Supera lo esperado"]) when no UmbralMateria is configured for the materia.

#### Scenario: Student with missing activities

- **WHEN** materia X has 3 activities (A1, A2, A3) and student S has calificaciones only for A1
- **THEN** student S is returned as atrasado with actividades_faltantes=["A2", "A3"]

#### Scenario: Student with nota below umbral

- **WHEN** materia X has umbral_pct=60 and student S has nota_numerica=45 in A1
- **THEN** student S is returned as atrasado with nota_baja_detalle containing A1=45

#### Scenario: Student with nota textual not in approved values

- **WHEN** materia X has valores_aprobatorios=["Satisfactorio", "Supera lo esperado"] and student S has nota_textual="Regular" in A1
- **THEN** student S is returned as atrasado with nota_baja_detalle containing A1="Regular"

#### Scenario: Student with no calificaciones at all

- **WHEN** materia X has 3 activities registered and student S has zero calificaciones
- **THEN** student S is returned as atrasado with all 3 activities listed as faltantes

#### Scenario: Student al dia (not atrasado)

- **WHEN** materia X has 3 activities, umbral_pct=60, and student S has calificaciones for all 3 with notas >= 60
- **THEN** student S is NOT included in the atrasados list

#### Scenario: Materia with no calificaciones

- **WHEN** materia X has zero calificaciones imported
- **THEN** the endpoint returns an empty list with status_info "Sin datos de calificaciones para esta materia"

#### Scenario: Materia with no umbral configured

- **WHEN** materia X has calificaciones but no UmbralMateria record exists
- **THEN** the system SHALL use default umbral_pct=60 and valores_aprobatorios=["Satisfactorio", "Supera lo esperado"]

#### Scenario: Tenant isolation

- **WHEN** tenant A requests atrasados for materia X and tenant B has calificaciones for the same materia
- **THEN** only tenant A's calificaciones are considered in the computation

### Requirement: Atrasados response schema

The system SHALL return a response with:
- `materia_id`: UUID
- `total_alumnos`: int — total students in the materia's active padrón
- `total_atrasados`: int
- `atrasados`: list of `AlumnoAtrasadoDTO` with `entrada_padron_id`, `nombre`, `apellidos`, `email`, `comision`, `regional`, `actividades_faltantes: list[str]`, `notas_bajas: list[NotaBajaDTO]`
- `status_info`: str | None — informational message when no data

#### Scenario: Valid response structure

- **WHEN** atrasados are computed successfully
- **THEN** the response conforms to the schema with all fields populated

#### Scenario: Extra fields rejected

- **WHEN** a response would include an undeclared field
- **THEN** Pydantic validation with `extra='forbid'` SHALL reject it
