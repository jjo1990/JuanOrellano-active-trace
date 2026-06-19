## ADDED Requirements

### Requirement: Exportar equipo docente a CSV
The system SHALL allow COORDINADOR and ADMIN to download a CSV file with the full detail of a teaching team, applying optional filters.

#### Scenario: Exportación con filtros de equipo
- **WHEN** COORDINADOR envía `GET /api/equipos/exportar?materia_id={uuid}&carrera_id={uuid}&cohorte_id={uuid}&vigente=true`
- **THEN** system returns 200 con `Content-Type: text/csv` y header `Content-Disposition: attachment; filename="equipo_docente.csv"`
- **AND** el CSV contiene columnas: `nombre`, `apellido`, `email`, `legajo`, `rol`, `materia`, `carrera`, `cohorte`, `comisiones`, `desde`, `hasta`, `estado`
- **AND** las filas corresponden solo a asignaciones que coinciden con los filtros

#### Scenario: Exportación sin filtros — no permitido
- **WHEN** COORDINADOR envía `GET /api/equipos/exportar` sin ningún filtro
- **THEN** system returns 400 Bad Request indicando que se requiere al menos un filtro (materia_id o carrera_id o cohorte_id)

#### Scenario: Estado derivado en exportación
- **WHEN** se exporta una asignación con `desde: 2026-03-01, hasta: 2026-07-31` y la fecha actual es 2026-06-15
- **THEN** la columna `estado` muestra "Vigente"
- **WHEN** se exporta una asignación con `desde: 2026-03-01, hasta: 2026-05-31` y la fecha actual es 2026-06-15
- **THEN** la columna `estado` muestra "Vencida"

#### Scenario: Sin permiso equipos:asignar
- **WHEN** usuario sin `equipos:asignar` envía `GET /api/equipos/exportar`
- **THEN** system returns 403 Forbidden

#### Scenario: Comisiones en CSV
- **WHEN** una asignación tiene `comisiones: ["A", "B"]`
- **THEN** la columna `comisiones` en el CSV muestra "A, B" (valores unidos por coma y espacio)

#### Scenario: Aislamiento multi-tenant en exportación
- **WHEN** COORDINADOR del tenant A exporta
- **THEN** el CSV solo contiene datos del tenant A
