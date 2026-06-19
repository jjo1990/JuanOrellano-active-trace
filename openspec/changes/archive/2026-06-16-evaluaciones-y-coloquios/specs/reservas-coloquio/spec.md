## ADDED Requirements

### Requirement: Reservar turno en convocatoria
El sistema SHALL permitir a un ALUMNO reservar un turno en una convocatoria con cupo disponible (HU-47).

#### Scenario: Reserva exitosa
- **WHEN** un ALUMNO envía `POST /api/coloquios/reservas` con `evaluacion_id` y `fecha_hora` de una convocatoria con cupo disponible
- **THEN** el sistema crea la reserva con estado Activa y el cupo disponible se reduce

#### Scenario: Reserva sin cupo disponible
- **WHEN** un ALUMNO intenta reservar en un día donde ya se alcanzó el `cupos_por_dia`
- **THEN** el sistema rechaza con 409 Conflict y mensaje "Cupo agotado para esta fecha"

#### Scenario: Reserva en convocatoria cerrada
- **WHEN** un ALUMNO intenta reservar en una convocatoria con estado Cerrada
- **THEN** el sistema rechaza con 422 y mensaje "La convocatoria está cerrada"

#### Scenario: Reserva duplicada del mismo alumno
- **WHEN** un ALUMNO que ya tiene una reserva Activa en la misma evaluación intenta reservar de nuevo
- **THEN** el sistema rechaza con 409 Conflict y mensaje "Ya tenés una reserva activa en esta convocatoria"

### Requirement: Cancelar reserva
El sistema SHALL permitir cancelar una reserva activa, liberando el cupo.

#### Scenario: ALUMNO cancela su reserva
- **WHEN** un ALUMNO envía `DELETE /api/coloquios/reservas/{id}` de su propia reserva Activa
- **THEN** el sistema cambia el estado a Cancelada

#### Scenario: Cancelar reserva de otro alumno
- **WHEN** un ALUMNO intenta cancelar una reserva de otro alumno
- **THEN** el sistema rechaza con 403

#### Scenario: COORDINADOR cancela cualquier reserva
- **WHEN** un COORDINADOR envía `DELETE /api/coloquios/reservas/{id}` de una reserva de cualquier alumno
- **THEN** el sistema cambia el estado a Cancelada

### Requirement: Agenda consolidada de reservas
El sistema SHALL permitir consultar todas las reservas activas con filtros (F7.5 agenda).

#### Scenario: COORDINADOR consulta agenda
- **WHEN** un COORDINADOR envía `GET /api/coloquios/agenda`
- **THEN** el sistema devuelve todas las reservas Activas del tenant con datos de alumno, materia y cohorte

#### Scenario: Filtrar agenda por materia
- **WHEN** un COORDINADOR envía `GET /api/coloquios/agenda?materia_id={id}`
- **THEN** el sistema devuelve solo reservas de esa materia

#### Scenario: Filtrar agenda por rango de fechas
- **WHEN** un COORDINADOR envía `GET /api/coloquios/agenda?fecha_desde=2026-06-01&fecha_hasta=2026-06-30`
- **THEN** el sistema devuelve solo reservas en ese rango

### Requirement: Control de acceso en reservas
El sistema SHALL requerir el permiso `coloquios:reservar` para crear o cancelar reservas como ALUMNO.

#### Scenario: Usuario sin permiso intenta reservar
- **WHEN** un PROFESOR sin permiso `coloquios:reservar` envía `POST /api/coloquios/reservas`
- **THEN** el sistema responde con 403
