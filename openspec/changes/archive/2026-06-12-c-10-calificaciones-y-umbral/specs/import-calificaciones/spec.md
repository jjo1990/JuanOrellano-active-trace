## ADDED Requirements

### Requirement: Import calificaciones from file

The system SHALL provide a two-step import pipeline for calificaciones from .xlsx and .csv files:
1. `POST /api/calificaciones/import` — upload, parse, detect column types, return preview token
2. `POST /api/calificaciones/confirm/<token>` — confirm with selected activities, persist Calificaciones

#### Scenario: Import xlsx with numeric columns
- **WHEN** a .xlsx file is uploaded with column headers including "Examen (Real)" and "TP (Real)"
- **THEN** the system SHALL detect these as numeric columns (RN-01: suffix "(Real)")

#### Scenario: Import csv with textual columns
- **WHEN** a .csv file is uploaded with column headers including "Satisfactorio" and "Supera lo esperado"
- **THEN** the system SHALL detect these as textual columns with `aprobatorio=True` (RN-02)

#### Scenario: Import preview returns token
- **WHEN** a valid file is uploaded via `POST /api/calificaciones/import`
- **THEN** the system SHALL return a `preview_token`, `detected_rows`, `columns` with types, `actividades`, and `preview_rows`

#### Scenario: Import preview columns response structure
- **WHEN** a file is parsed
- **THEN** each column in the response SHALL include: `name`, `tipo` ("numerica" | "textual"), and `aprobatorio` (bool)

#### Scenario: Confirm import persists Calificaciones
- **WHEN** `POST /api/calificaciones/confirm/<token>` is called with `actividades_seleccionadas=["Examen (Real)"]`
- **THEN** the system SHALL persist Calificaciones for each EntradaPadron in the active version, matching rows by nombre+apellidos

#### Scenario: Confirm import ignores rows without matching EntradaPadron
- **WHEN** a file row has a student name that doesn't match any EntradaPadron in the active version
- **THEN** the system SHALL skip that row and include it in the `ignorados` response field

#### Scenario: Confirm import with invalid token
- **WHEN** `POST /api/calificaciones/confirm/<token>` is called with an expired or invalid token
- **THEN** the system SHALL return 404

#### Scenario: Confirm import registers audit log
- **WHEN** calificaciones are imported successfully
- **THEN** the system SHALL register an audit log with action `CALIFICACIONES_IMPORTAR`

#### Scenario: Import without permission
- **WHEN** a request is made to `/api/calificaciones/import` without `calificaciones:importar` permission
- **THEN** the system SHALL return 403

#### Scenario: Upload with unsupported format
- **WHEN** a file with extension other than .xlsx or .csv is uploaded
- **THEN** the system SHALL return 422

### Requirement: Column detection RN-01

Columns whose name ends in "(Real)" SHALL be classified as `tipo: "numerica"`.

#### Scenario: Detect (Real) suffix
- **WHEN** a column is named "Examen Final (Real)"
- **THEN** `_detect_column_types()` SHALL set `tipo="numerica"`
- **WHEN** a column is named "Nota Practica (Real)"
- **THEN** `_detect_column_types()` SHALL set `tipo="numerica"`

### Requirement: Column detection RN-02

Columns named "Satisfactorio" or "Supera lo esperado" SHALL be classified as `tipo: "textual"` with `aprobatorio=True`.

#### Scenario: Detect Satisfactorio column
- **WHEN** a column is named "Satisfactorio"
- **THEN** `_detect_column_types()` SHALL set `tipo="textual"` and `aprobatorio=True`

#### Scenario: Detect Supera lo esperado column
- **WHEN** a column is named "Supera lo esperado"
- **THEN** `_detect_column_types()` SHALL set `tipo="textual"` and `aprobatorio=True`
