## ADDED Requirements

### Requirement: BaseModelMixin con UUID como PK

Toda entidad del sistema SHALL heredar de un mixin `BaseModelMixin` que provea un campo `id` de tipo UUID como clave primaria. El UUID SHALL generarse en la aplicación con `uuid.uuid4()`, no en la base de datos.

#### Scenario: UUID auto-generado al crear entidad

- **WHEN** se instancia una entidad que hereda de `BaseModelMixin`
- **THEN** su campo `id` contiene un UUID válido generado por la aplicación
- **AND** cada instancia tiene un UUID diferente

### Requirement: tenant_id obligatorio en toda entidad

`BaseModelMixin` SHALL incluir un campo `tenant_id` de tipo UUID (FK → Tenant) que identifica al tenant propietario. Este campo SHALL ser obligatorio (no nulo) para todas las entidades excepto para el modelo Tenant mismo.

#### Scenario: Entidad se crea con tenant_id

- **GIVEN** un tenant existente
- **WHEN** se crea una entidad que hereda de `BaseModelMixin`
- **THEN** la entidad queda asociada al tenant mediante su `tenant_id`
- **AND** no es posible crear una entidad sin `tenant_id`

### Requirement: Timestamps automáticos

`BaseModelMixin` SHALL incluir los campos `created_at` (datetime, default=now) y `updated_at` (datetime, se actualiza en cada modificación).

#### Scenario: created_at y updated_at en creación

- **WHEN** se crea una nueva entidad
- **THEN** `created_at` y `updated_at` se establecen automáticamente al momento actual
- **AND** son del tipo datetime con zona horaria

#### Scenario: updated_at se actualiza al modificar

- **GIVEN** una entidad existente con `updated_at = T1`
- **WHEN** se modifica la entidad
- **THEN** `updated_at` cambia a un valor posterior a T1

### Requirement: Soft delete en el mixin

`BaseModelMixin` SHALL incluir un campo `deleted_at` de tipo datetime nullable. Cuando es nulo, la entidad está activa. Cuando tiene valor, la entidad está eliminada lógicamente.

#### Scenario: Soft delete marca deleted_at

- **GIVEN** una entidad activa con `deleted_at IS NULL`
- **WHEN** se ejecuta soft delete sobre la entidad
- **THEN** `deleted_at` se establece al momento actual
- **AND** la entidad continúa existiendo en la base de datos
