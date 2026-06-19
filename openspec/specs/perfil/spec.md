# perfil Specification

## Purpose
TBD - created by archiving change perfil-y-mensajeria-interna. Update Purpose after archive.
## Requirements
### Requirement: Usuario autenticado puede consultar su perfil

El sistema SHALL permitir a cualquier usuario autenticado obtener los datos completos de su perfil, incluyendo datos PII descifrados (DNI, CUIL, CBU, alias CBU) que son propiedad del usuario.

#### Scenario: Consulta exitosa del perfil propio

- **WHEN** un usuario autenticado realiza `GET /api/perfil`
- **THEN** el sistema retorna 200 con todos los campos del perfil: id, tenant_id, nombre, apellidos, email, dni, cuil, cbu, alias_cbu, banco, regional, legajo, legajo_profesional, facturador, activo, created_at, updated_at

#### Scenario: Usuario no autenticado consulta perfil

- **WHEN** una petición sin token JWT válido realiza `GET /api/perfil`
- **THEN** el sistema retorna 401 Unauthorized

### Requirement: Usuario autenticado puede editar su perfil

El sistema SHALL permitir a cualquier usuario autenticado modificar los campos editables de su perfil mediante `PATCH /api/perfil`. El CUIL es de solo lectura y no puede modificarse por este endpoint. Los campos PII (DNI, CBU, alias CBU) se reciben en texto plano y se cifran automáticamente en reposo.

#### Scenario: Edición exitosa de campos del perfil

- **WHEN** un usuario autenticado envía `PATCH /api/perfil` con `{"nombre": "Carlos", "banco": "Santander", "facturador": true}`
- **THEN** el sistema actualiza los campos especificados, conserva los no especificados, y retorna 200 con el perfil completo actualizado

#### Scenario: Intento de modificar CUIL

- **WHEN** un usuario autenticado envía `PATCH /api/perfil` con `{"cuil": "20-12345678-9"}`
- **THEN** el sistema retorna 422 Unprocessable Entity porque el campo `cuil` no está declarado en el schema `PerfilUpdate` (`extra='forbid'`)

#### Scenario: Email duplicado dentro del mismo tenant

- **WHEN** un usuario autenticado envía `PATCH /api/perfil` con un `email` que ya pertenece a otro usuario del mismo tenant
- **THEN** el sistema retorna 409 Conflict con mensaje descriptivo

#### Scenario: Intento de modificar contraseña por perfil

- **WHEN** un usuario autenticado envía `PATCH /api/perfil` con `{"password": "nueva123"}`
- **THEN** el sistema retorna 422 Unprocessable Entity porque `password` no está declarado en el schema `PerfilUpdate`

#### Scenario: Intento de modificar campo activo por perfil

- **WHEN** un usuario autenticado envía `PATCH /api/perfil` con `{"activo": false}`
- **THEN** el sistema retorna 422 Unprocessable Entity porque `activo` no está declarado en el schema `PerfilUpdate`

### Requirement: Respuesta de perfil incluye PII descifrado

El sistema SHALL retornar los datos PII (DNI, CUIL, CBU, alias CBU) en texto plano en la respuesta del perfil propio, ya que el dueño de los datos tiene derecho a verlos.

#### Scenario: Perfil propio incluye DNI descifrado

- **WHEN** un usuario autenticado consulta `GET /api/perfil`
- **THEN** la respuesta incluye el campo `dni` con el valor descifrado (no el valor cifrado de la columna `dni_encrypted`)

#### Scenario: Perfil propio incluye CUIL descifrado (solo lectura)

- **WHEN** un usuario autenticado consulta `GET /api/perfil`
- **THEN** la respuesta incluye el campo `cuil` con el valor descifrado, y este campo no es modificable vía `PATCH`

