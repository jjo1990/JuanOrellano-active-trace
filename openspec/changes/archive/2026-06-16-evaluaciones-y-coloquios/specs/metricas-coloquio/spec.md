## ADDED Requirements

### Requirement: Panel de métricas de coloquios
El sistema SHALL exponer un panel de métricas agregadas con totales del estado de situación de las evaluaciones orales (F7.1).

#### Scenario: COORDINADOR consulta métricas generales
- **WHEN** un COORDINADOR envía `GET /api/coloquios/metricas`
- **THEN** el sistema devuelve: `total_alumnos_cargados`, `total_instancias_activas`, `total_reservas_activas`, `total_notas_registradas`

#### Scenario: Filtrar métricas por cohorte
- **WHEN** un COORDINADOR envía `GET /api/coloquios/metricas?cohorte_id={id}`
- **THEN** el sistema devuelve las métricas acotadas a esa cohorte

#### Scenario: Sin datos
- **WHEN** un COORDINADOR consulta métricas y no hay evaluaciones creadas
- **THEN** el sistema devuelve todos los totales en 0

### Requirement: Control de acceso en métricas
El sistema SHALL requerir el permiso `coloquios:gestionar` para acceder al panel de métricas.

#### Scenario: Usuario sin permiso intenta acceder
- **WHEN** un ALUMNO envía `GET /api/coloquios/metricas`
- **THEN** el sistema responde con 403
