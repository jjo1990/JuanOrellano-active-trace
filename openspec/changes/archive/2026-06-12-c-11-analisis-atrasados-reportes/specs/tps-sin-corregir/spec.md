## ADDED Requirements

### Requirement: Detect ungraded textual submissions

The system SHALL provide an endpoint `GET /api/analisis/sin-corregir/{materia_id}` that returns activities completed by students but not yet graded.

The endpoint SHALL accept a query parameter `reporte_token` referencing a previously imported finalization report (from C-10's `POST /api/calificaciones/import-finalizacion`).

The system SHALL apply RN-08: only textual-scale (cualitativa) activities are included. Activities with numeric scale are excluded because absence of a numeric nota means "not submitted", not "pending correction".

The system SHALL cross-reference:
1. Load the finalization report from the preview cache using `reporte_token`.
2. For each (student, activity) marked as completed in the report.
3. Check if the student has a `Calificacion` with `nota_textual` for that activity.
4. If no calificacion exists → include in "sin corregir" list.

#### Scenario: Student completed but not graded

- **WHEN** finalization report shows student S completed activity "TP1" and student S has no calificacion for "TP1"
- **THEN** student S appears in sin-corregir list for activity "TP1"

#### Scenario: Student completed and graded

- **WHEN** finalization report shows student S completed "TP1" and student S has nota_textual="Satisfactorio" for "TP1"
- **THEN** student S does NOT appear in sin-corregir list for "TP1"

#### Scenario: Numeric activity excluded

- **WHEN** the finalization report includes an activity "Parcial 1" that is numeric-scale in calificaciones (has nota_numerica values)
- **THEN** "Parcial 1" is excluded from the sin-corregir computation

#### Scenario: Invalid or expired reporte_token

- **WHEN** the `reporte_token` is not found in the preview cache (expired or invalid)
- **THEN** the endpoint SHALL return 404 with detail "Reporte de finalización no encontrado o expirado"

#### Scenario: No finalization report provided

- **WHEN** the endpoint is called without `reporte_token`
- **THEN** the endpoint SHALL return 400 with detail "Se requiere reporte_token del reporte de finalización"

#### Scenario: TPs sin corregir response schema

- **WHEN** sin-corregir is computed
- **THEN** the response SHALL contain `materia_id`, `total_sin_corregir`, `entregas: list[EntregaSinCorregirDTO]` with fields `entrada_padron_id`, `nombre`, `apellidos`, `email`, `comision`, `actividad`, `fecha_finalizacion`

#### Scenario: Tenant isolation

- **WHEN** tenant A requests sin-corregir and the reporte_token belongs to tenant A
- **THEN** only tenant A's calificaciones are considered
