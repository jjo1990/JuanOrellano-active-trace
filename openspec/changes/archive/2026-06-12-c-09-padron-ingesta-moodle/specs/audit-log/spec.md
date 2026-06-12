## ADDED Requirements

### Requirement: Audit action PADRON_CARGAR

El sistema SHALL registrar en el audit log todas las operaciones de importación y vaciado de padrón con la acción `PADRON_CARGAR`. Cada registro SHALL incluir materia_id, versión afectada, cantidad de filas y tipo de operación (import/confirm/vaciar).

#### Scenario: Registro al importar padrón

- **GIVEN** un import de padrón exitoso (confirmado)
- **WHEN** se persisten las entradas
- **THEN** se crea un AuditLog con `accion = "PADRON_CARGAR"`
- **AND** el detalle incluye `{tipo: "import", materia_id: ..., version_id: ..., filas: N}`

#### Scenario: Registro al vaciar materia

- **GIVEN** un vaciado de materia exitoso
- **WHEN** se ejecuta soft delete de las entradas
- **THEN** se crea un AuditLog con `accion = "PADRON_CARGAR"`
- **AND** el detalle incluye `{tipo: "vaciar", materia_id: ..., version_id: ..., filas_afectadas: N}`
