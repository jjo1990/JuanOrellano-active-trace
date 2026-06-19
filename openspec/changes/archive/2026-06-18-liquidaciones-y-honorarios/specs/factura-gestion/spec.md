## ADDED Requirements

### Requirement: ABM de facturas
El sistema SHALL permitir a FINANZAS crear, consultar, modificar y eliminar (soft delete) registros de `Factura` para docentes monotributistas (RN-39, RN-40).

#### Scenario: Crear factura
- **WHEN** FINANZAS envía `POST /api/facturas` con `usuario_id=<docente>`, `periodo=2026-06`, `detalle="Honorarios junio"`, `referencia_archivo=<path>`, `tamano_kb=150`
- **THEN** el sistema crea la factura con `estado=Pendiente`, `cargada_at=now()`, y retorna 201.

#### Scenario: Crear factura para docente no facturante
- **WHEN** el `usuario_id` corresponde a un docente con `modalidad_pago=relacion_dependencia`
- **THEN** el sistema retorna 422 con mensaje "El docente no está configurado como facturante".

### Requirement: Cambio de estado de factura
El sistema SHALL permitir transicionar una factura entre `Pendiente` y `Abonada`.

#### Scenario: Marcar factura como abonada
- **WHEN** FINANZAS solicita `POST /api/facturas/{id}/abonar`
- **THEN** el sistema cambia `estado=Abonada`, registra `abonada_at=now()`, crea auditoría `FACTURA_ABONAR`, y retorna 200.

#### Scenario: Marcar factura abonada como pendiente
- **WHEN** FINANZAS solicita `POST /api/facturas/{id}/marcar-pendiente` sobre una factura abonada
- **THEN** el sistema cambia `estado=Pendiente`, limpia `abonada_at=null`, y retorna 200.

### Requirement: Listado de facturas con filtros
El sistema SHALL permitir listar facturas con filtros por docente, estado, período y rango de fechas.

#### Scenario: Listado filtrado por estado y período
- **WHEN** se solicita `GET /api/facturas?estado=Pendiente&periodo=2026-06`
- **THEN** el sistema retorna 200 con array de facturas que coinciden con los filtros.

#### Scenario: Búsqueda por docente
- **WHEN** se solicita `GET /api/facturas?usuario_id=<id>`
- **THEN** el sistema retorna solo las facturas de ese docente.

### Requirement: Factura no modificable en campos core después de creada
El sistema SHALL permitir modificar solo `detalle`, `referencia_archivo` y `tamano_kb` de una factura existente. `usuario_id` y `periodo` son inmutables.

#### Scenario: Intento de cambiar período
- **WHEN** se intenta `PUT /api/facturas/{id}` con `periodo` distinto al original
- **THEN** el sistema retorna 422.
