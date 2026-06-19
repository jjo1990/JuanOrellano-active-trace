## ADDED Requirements

### Requirement: Registrar fecha académica
El sistema SHALL permitir registrar fechas de evaluaciones por materia, cohorte, tipo y número de instancia (F5.4, HU-24).

#### Scenario: Registrar fecha de parcial
- **WHEN** COORDINADOR envía `POST /api/fechas-academicas` con materia_id, cohorte_id, tipo=Parcial, numero=1, fecha, titulo
- **THEN** el sistema crea la fecha académica

#### Scenario: Registrar coloquio
- **WHEN** COORDINADOR envía con tipo=Coloquio, numero=1
- **THEN** el sistema crea el registro

### Requirement: Listar fechas en tabla
El sistema SHALL listar fechas académicas en formato tabular con filtros por materia, cohorte y tipo.

#### Scenario: Tabla filtrada por cohorte
- **WHEN** `GET /api/fechas-academicas?cohorte_id=X`
- **THEN** devuelve fechas de esa cohorte ordenadas por fecha ASC

### Requirement: Vista calendario
El sistema SHALL agrupar fechas por mes para vista calendario.

#### Scenario: Calendario agrupado
- **WHEN** `GET /api/fechas-academicas/calendario?cohorte_id=X`
- **THEN** devuelve fechas agrupadas por mes (ej: "2026-03": [fechas de marzo])

### Requirement: Cronograma HTML para LMS
El sistema SHALL generar un fragmento HTML con el cronograma de evaluaciones listo para el aula virtual.

#### Scenario: Generar cronograma
- **WHEN** `GET /api/fechas-academicas/cronograma-lms?materia_id=X&cohorte_id=Y`
- **THEN** devuelve HTML con tabla de fechas agrupadas por tipo

### Requirement: Editar y eliminar fechas
El sistema SHALL permitir modificar y soft-deletear fechas académicas.

### Requirement: Aislamiento multi-tenant
El sistema SHALL aislar fechas por tenant.
