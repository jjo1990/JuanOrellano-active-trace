## ADDED Requirements

### Requirement: Modelo Tenant como entidad raíz

El sistema SHALL modelar un Tenant como la entidad raíz del sistema. Cada institución usuaria SHALL estar representada por un único registro Tenant. Toda otra entidad del sistema SHALL pertenecer a exactamente un Tenant. No SHALL existir datos huerfanos sin tenant.

#### Scenario: Creación de un Tenant

- **GIVEN** un slug único que no existe en el sistema
- **WHEN** se crea un Tenant con ese slug
- **THEN** el Tenant se guarda con un UUID único generado por la aplicación
- **AND** los campos `created_at` y `updated_at` se establecen automáticamente
- **AND** `deleted_at` es nulo

#### Scenario: Slug duplicado es rechazado

- **GIVEN** un Tenant existente con slug `"universidad-a"`
- **WHEN** se intenta crear otro Tenant con slug `"universidad-a"`
- **THEN** la operación falla con un error de unicidad

### Requirement: Configuración por tenant

El modelo Tenant SHALL incluir un campo `config` de tipo JSONB que almacene la configuración específica del tenant: idioma, marca, umbrales por defecto, plantillas y flags de funcionalidad.

#### Scenario: Config con valores por defecto

- **WHEN** se crea un Tenant sin especificar `config`
- **THEN** se guarda con un objeto JSON vacío `{}` como valor por defecto

### Requirement: Soft delete en Tenant

Tenant SHALL soportar soft delete. Al eliminar un Tenant, su campo `deleted_at` SHALL establecerse al timestamp actual. El Tenant no SHALL desaparecer de la base de datos.

#### Scenario: Soft delete de Tenant

- **GIVEN** un Tenant activo
- **WHEN** se ejecuta soft delete sobre ese Tenant
- **THEN** `deleted_at` se establece al momento actual
- **AND** el registro continúa existiendo en la base de datos
