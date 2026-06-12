## ADDED Requirements

### Requirement: GET umbral by materia

The system SHALL provide `GET /api/calificaciones/umbral/<materia_id>` to retrieve the configured umbral for a materia, scoped by asignacion.

The endpoint SHALL accept `asignacion_id` as a query parameter.

#### Scenario: GET umbral when configured
- **WHEN** a GET request is made with a materia_id that has a configured UmbralMateria
- **THEN** the system SHALL return the umbral record with umbral_pct, valores_aprobatorios, materia_id, asignacion_id

#### Scenario: GET umbral when NOT configured
- **WHEN** a GET request is made with a materia_id that has NO configured UmbralMateria
- **THEN** the system SHALL return default values: `umbral_pct=60`, `valores_aprobatorios=["Satisfactorio", "Supera lo esperado"]`

#### Scenario: GET umbral without permission
- **WHEN** a GET request is made without `calificaciones:importar` permission
- **THEN** the system SHALL return 403

#### Scenario: GET umbral tenant isolation
- **WHEN** tenant A has an umbral configured for materia X, and tenant B requests it
- **THEN** tenant B SHALL receive defaults (no umbral configured), not tenant A's umbral

### Requirement: PUT umbral by materia

The system SHALL provide `PUT /api/calificaciones/umbral/<materia_id>` to create or update the umbral for a materia.

The endpoint SHALL accept `asignacion_id` as a query parameter and a JSON body with `umbral_pct` and `valores_aprobatorios`.

#### Scenario: PUT creates new umbral
- **WHEN** a PUT request is made for a (materia_id, asignacion_id) without an existing umbral
- **THEN** the system SHALL create a new UmbralMateria with the provided values

#### Scenario: PUT updates existing umbral
- **WHEN** a PUT request is made for a (materia_id, asignacion_id) with an existing umbral
- **THEN** the system SHALL update umbral_pct and valores_aprobatorios

#### Scenario: PUT with invalid umbral_pct
- **WHEN** `umbral_pct` is less than 0 or greater than 100
- **THEN** the system SHALL return 422

#### Scenario: PUT without permission
- **WHEN** a PUT request is made without `calificaciones:importar` permission
- **THEN** the system SHALL return 403
