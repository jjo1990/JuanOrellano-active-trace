## ADDED Requirements

### Requirement: Vaciar datos de materia (RN-04, F1.5)

El sistema SHALL permitir vaciar (eliminar lógicamente) todos los datos de ingesta y calificaciones de una materia. El alcance SHALL estar scoped por `(usuario_id, materia_id)` — un profesor solo puede vaciar sus propias materias; un coordinador puede vaciar cualquier materia del tenant. SHALL usar soft delete.

#### Scenario: Profesor vacía su materia

- **GIVEN** un profesor con asignación a la materia M
- **WHEN** envía `DELETE /api/padron/vaciar/<materia_id>`
- **THEN** se aplica soft delete a todas las VersionPadron y EntradaPadron de esa materia
- **AND** se registra audit log con acción `PADRON_CARGAR` y detalle "vaciar materia"
- **AND** el profesor está autorizado porque tiene asignación a la materia

#### Scenario: Coordinador vacía cualquier materia

- **GIVEN** un coordinador sin asignación directa a la materia M
- **WHEN** envía `DELETE /api/padron/vaciar/<materia_id>`
- **THEN** puede vaciar la materia igualmente (permiso global)
- **AND** se registra audit log

#### Scenario: Profesor intenta vaciar materia no asignada

- **GIVEN** un profesor sin asignación a la materia M
- **WHEN** envía `DELETE /api/padron/vaciar/<materia_id>`
- **THEN** el sistema retorna 403 Forbidden

#### Scenario: Vaciar materia preserva la materia misma

- **GIVEN** una materia con datos de padrón y calificaciones
- **WHEN** se ejecuta vaciar materia
- **THEN** la materia no se elimina
- **AND** solo se marcan como deleted_at las entradas de padrón y calificaciones asociadas
