## ADDED Requirements

### Requirement: Clonar equipo docente entre cohortes (RN-12)
The system SHALL duplicate all non-deleted asignaciones from an origin team (materia × carrera × cohorte origen) to a destination team (misma materia, misma carrera, diferente cohorte), applying RN-12.

#### Scenario: Clonación exitosa de equipo
- **WHEN** COORDINADOR envía `POST /api/equipos/clonar` con `{materia_id: uuid, carrera_id: uuid, cohorte_origen_id: uuid, cohorte_destino_id: uuid, desde: "2026-08-01", hasta: "2026-12-31"}`
- **THEN** system returns 201 con `{asignaciones_creadas: [...], total_clonadas: N}`
- **AND** se duplican todas las asignaciones no eliminadas del equipo origen
- **AND** cada asignación nueva conserva `usuario_id`, `rol_id`, `materia_id`, `carrera_id`, `comisiones`, `responsable_id` del origen
- **AND** `cohorte_id` se setea al destino
- **AND** `desde` y `hasta` se setean a las fechas indicadas en el request (no se heredan del origen)
- **AND** cada asignación nueva tiene un `id` UUID nuevo (no se hereda el ID del origen)

#### Scenario: Clonación con equipo origen sin asignaciones
- **WHEN** COORDINADOR envía `POST /api/equipos/clonar` con un origen que no tiene asignaciones
- **THEN** system returns 201 con `{asignaciones_creadas: [], total_clonadas: 0}`

#### Scenario: Clonación ignora asignaciones eliminadas
- **WHEN** el equipo origen tiene 5 asignaciones de las cuales 2 están soft-deleteadas
- **THEN** system clona solo las 3 asignaciones no eliminadas
- **AND** `total_clonadas` es 3

#### Scenario: Sin permiso equipos:asignar
- **WHEN** usuario sin `equipos:asignar` envía `POST /api/equipos/clonar`
- **THEN** system returns 403 Forbidden

#### Scenario: Cohorte destino inválida
- **WHEN** COORDINADOR envía `POST /api/equipos/clonar` con `cohorte_destino_id` que no existe
- **THEN** system returns 404 indicando que la cohorte destino no fue encontrada

#### Scenario: Cohorte origen y destino iguales
- **WHEN** COORDINADOR envía `POST /api/equipos/clonar` con `cohorte_origen_id == cohorte_destino_id`
- **THEN** system returns 400 Bad Request indicando que origen y destino deben ser diferentes

#### Scenario: Aislamiento multi-tenant en clonación
- **WHEN** COORDINADOR del tenant A intenta clonar desde un equipo que pertenece al tenant B
- **THEN** system no encuentra asignaciones (el filtro de tenant_id del repositorio retorna vacío) y `total_clonadas` es 0
