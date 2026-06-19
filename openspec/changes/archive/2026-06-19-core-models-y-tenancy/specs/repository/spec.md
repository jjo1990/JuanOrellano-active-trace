## ADDED Requirements

### Requirement: Repository genérico con scope de tenant

El sistema SHALL proveer una clase `Repository[T]` genérica, abstracta, que implemente operaciones CRUD básicas. Toda operación SHALL filtrar por `tenant_id` de forma obligatoria. El `tenant_id` SHALL inyectarse en el constructor del Repository, no por parámetro en cada método, garantizando que ningún método pueda omitir el filtro de tenant.

#### Scenario: Get filtra por tenant

- **GIVEN** dos tenants A y B
- **AND** una entidad con `id=ID1` pertenece al tenant A
- **WHEN** el repository del tenant A ejecuta `get(id=ID1)`
- **THEN** retorna la entidad
- **WHEN** el repository del tenant B ejecuta `get(id=ID1)`
- **THEN** retorna None (la entidad no pertenece al tenant B)

#### Scenario: List solo retorna entidades del tenant

- **GIVEN** entidades en los tenants A y B
- **WHEN** el repository del tenant A ejecuta `list()`
- **THEN** solo retorna entidades del tenant A
- **AND** no incluye entidades del tenant B

#### Scenario: Create asigna tenant_id automáticamente

- **GIVEN** un repository del tenant A
- **WHEN** se ejecuta `create(entity)` donde la entidad tiene `tenant_id = None`
- **THEN** el repository asigna `tenant_id = UUID_de_A` antes de persistir

### Requirement: Soft delete en list por defecto

El método `list()` del Repository SHALL excluir por defecto las entidades con `deleted_at IS NOT NULL`.

#### Scenario: List excluye entidades eliminadas

- **GIVEN** 3 entidades activas y 1 entidad con soft delete en el mismo tenant
- **WHEN** se ejecuta `list()`
- **THEN** retorna solo las 3 entidades activas
- **AND** no incluye la entidad con soft delete

### Requirement: Update verifica tenant

El método `update(entity)` SHALL verificar que la entidad a actualizar pertenece al tenant del repository.

#### Scenario: Update rechaza entidad de otro tenant

- **GIVEN** una entidad del tenant B
- **WHEN** el repository del tenant A intenta `update(entity)`
- **THEN** la operación falla con un error (raise o retorna None)
- **AND** la entidad no se modifica en la base de datos

### Requirement: Soft delete verifica tenant

El método `soft_delete(id)` SHALL verificar que la entidad pertenece al tenant antes de marcarla como eliminada.

#### Scenario: Soft delete rechaza entidad de otro tenant

- **GIVEN** una entidad del tenant B con id ID2
- **WHEN** el repository del tenant A ejecuta `soft_delete(id=ID2)`
- **THEN** la operación falla o retorna que no se encontró
- **AND** la entidad del tenant B no se modifica
