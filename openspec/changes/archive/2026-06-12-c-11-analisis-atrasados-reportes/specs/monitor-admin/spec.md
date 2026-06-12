## ADDED Requirements

### Requirement: Admin monitor with date range

The system SHALL provide an endpoint `GET /api/analisis/monitor/admin` that extends the seguimiento monitor with an additional date range filter for COORD/ADMIN roles.

The endpoint SHALL accept all seguimiento query parameters PLUS:
- `fecha_desde`: date — filter calificaciones imported on or after this date
- `fecha_hasta`: date — filter calificaciones imported on or before this date

The system SHALL use the `importado_at` field on `Calificacion` to apply the date range.

When date range is applied, only calificaciones within the range are considered for computing estado, aprobadas, and faltantes.

The endpoint SHALL return all students across the tenant (not scoped to teacher asignacion), similar to monitor-general but with the date range capability.

#### Scenario: Date range filters calificaciones

- **WHEN** admin monitor is called with `fecha_desde=2026-03-01` and `fecha_hasta=2026-03-31`
- **THEN** only calificaciones with importado_at within March 2026 are considered

#### Scenario: Date range excludes old calificaciones

- **WHEN** student S has 5 approved calificaciones but only 2 were imported within the date range
- **THEN** aprobadas = 2 for student S

#### Scenario: Only fecha_desde provided

- **WHEN** admin monitor is called with `fecha_desde=2026-03-01` and no fecha_hasta
- **THEN** calificaciones from March 1 2026 onwards are considered

#### Scenario: No date range acts like monitor-general

- **WHEN** admin monitor is called without date range params
- **THEN** all calificaciones are considered (same behavior as monitor-general)

#### Scenario: Admin monitor response schema

- **WHEN** the admin monitor is computed
- **THEN** the response SHALL contain `total`, `rango_fechas: {desde, hasta} | null`, `estudiantes: list[AdminMonitorEntryDTO]` with the same fields as SeguimientoEntryDTO

#### Scenario: Tenant isolation

- **WHEN** admin in tenant A requests the admin monitor
- **THEN** only tenant A's data is returned
