## ADDED Requirements

### Requirement: Modificar vigencia de todas las asignaciones de un equipo en una operación
The system SHALL allow COORDINADOR and ADMIN to update `desde` and/or `hasta` for all asignaciones matching a team filter (materia × carrera × cohorte) in a single operation.

#### Scenario: Actualización masiva de fechas
- **WHEN** COORDINADOR envía `PUT /api/equipos/vigencia` con `{materia_id: uuid, carrera_id: uuid, cohorte_id: uuid, desde: "2026-08-01", hasta: "2026-12-31"}`
- **THEN** system returns 200 con `{asignaciones_actualizadas: N, total_encontradas: N}`
- **AND** todas las asignaciones no eliminadas que coinciden con el filtro tienen su `desde` y `hasta` actualizados

#### Scenario: Actualizar solo desde sin modificar hasta
- **WHEN** COORDINADOR envía `PUT /api/equipos/vigencia` con `{..., desde: "2026-08-01"}` sin incluir `hasta`
- **THEN** system returns 200 con solo `desde` actualizado en cada asignación
- **AND** `hasta` se mantiene sin cambios

#### Scenario: Sin permiso equipos:asignar
- **WHEN** usuario sin `equipos:asignar` envía `PUT /api/equipos/vigencia`
- **THEN** system returns 403 Forbidden

#### Scenario: Equipo sin asignaciones
- **WHEN** COORDINADOR envía `PUT /api/equipos/vigencia` para un equipo (materia × carrera × cohorte) sin asignaciones
- **THEN** system returns 200 con `{asignaciones_actualizadas: 0, total_encontradas: 0}`

#### Scenario: Fecha desde posterior a hasta
- **WHEN** COORDINADOR envía `PUT /api/equipos/vigencia` con `desde > hasta`
- **THEN** system returns 400 Bad Request

#### Scenario: Filtro parcial — sin materia_id
- **WHEN** COORDINADOR envía `PUT /api/equipos/vigencia` sin `materia_id` (solo `carrera_id` y `cohorte_id`)
- **THEN** system returns 200 actualizando todas las asignaciones que coinciden con el filtro parcial
- **AND** los tres filtros son opcionales; se requiere al menos uno para evitar actualización masiva sin scope

#### Scenario: Aislamiento multi-tenant
- **WHEN** COORDINADOR del tenant A modifica vigencia
- **THEN** solo se afectan asignaciones del tenant A
