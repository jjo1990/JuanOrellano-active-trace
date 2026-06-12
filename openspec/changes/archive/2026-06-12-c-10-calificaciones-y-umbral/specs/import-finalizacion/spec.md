## ADDED Requirements

### Requirement: Import finalizacion report (F1.2)

The system SHALL provide `POST /api/calificaciones/import-finalizacion` to import completion/finalization reports from the LMS.

This endpoint SHALL detect rows representing finalized deliveries without numeric grades and store them as `Calificacion` records with an appropriate `nota_textual` indicating the completion state.

#### Scenario: Import finalizacion report
- **WHEN** a .xlsx file is uploaded with columns "Nombre", "Apellidos", and "Estado" (with values like "Finalizado", "Incompleto")
- **THEN** the system SHALL create Calificacion records with `nota_textual` set to the estado value and `nota_numerica=None`

#### Scenario: Import finalizacion stores origen as Importado
- **WHEN** records are created via `/import-finalizacion`
- **THEN** `origen` SHALL be set to `"Importado"`

#### Scenario: Import finalizacion ignores non-finalized rows
- **WHEN** a row has "Estado" = "En curso"
- **THEN** the system SHALL NOT create a Calificacion for that row and SHALL include it in `ignorados`

#### Scenario: Import finalizacion registers audit log
- **WHEN** finalizacion import completes successfully
- **THEN** the system SHALL register an audit log with action `CALIFICACIONES_IMPORTAR`
