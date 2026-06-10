## ADDED Requirements

### Requirement: Admin puede crear usuario
The system SHALL allow ADMIN users to create new users within their tenant.

#### Scenario: Creación exitosa con todos los campos
- **WHEN** ADMIN envía POST `/api/admin/usuarios` con `{nombre, apellidos, email, password, dni, cuil, cbu, alias_cbu, banco, regional, legajo, legajo_profesional, facturador, activo}`
- **THEN** system returns 201 con el usuario creado (sin PII en texto plano en la response)
- **AND** el usuario se persiste en `user` table
- **AND** `dni`, `cuil`, `cbu`, `alias_cbu` se almacenan cifrados con AES-256-GCM

#### Scenario: Creación con solo campos requeridos
- **WHEN** ADMIN envía POST `/api/admin/usuarios` con solo `{nombre, apellidos, email, password}`
- **THEN** system returns 201
- **AND** `facturador` defaults a `false`, `activo` defaults a `true`

#### Scenario: Email duplicado en el mismo tenant
- **WHEN** ADMIN crea un usuario con email que ya existe en el tenant
- **THEN** system returns 409 Conflict
- **AND** mensaje de error indica que el email ya está registrado

#### Scenario: Email duplicado en distinto tenant
- **WHEN** ADMIN del tenant A crea usuario con email que existe en tenant B
- **THEN** system returns 201
- **AND** la unicidad es por `(tenant_id, email)`

#### Scenario: Sin permiso usuarios:gestionar
- **WHEN** usuario sin permiso `usuarios:gestionar` intenta crear un usuario
- **THEN** system returns 403 Forbidden

### Requirement: Admin puede listar usuarios
The system SHALL allow ADMIN to list all users in their tenant with pagination and filters.

#### Scenario: Listado paginado
- **WHEN** ADMIN envía GET `/api/admin/usuarios?page=1&per_page=20`
- **THEN** system returns 200 con lista de usuarios (sin PII en texto plano)
- **AND** response incluye `{items: [], total, page, per_page}`

#### Scenario: Filtro por estado activo/inactivo
- **WHEN** ADMIN envía GET `/api/admin/usuarios?activo=true`
- **THEN** system returns 200 con solo usuarios activos

#### Scenario: Filtro por búsqueda de texto
- **WHEN** ADMIN envía GET `/api/admin/usuarios?q=García`
- **THEN** system returns 200 con usuarios cuyo nombre o apellidos contienen "García"

#### Scenario: Aislamiento multi-tenant
- **WHEN** ADMIN del tenant A lista usuarios
- **THEN** system returns 200 con solo usuarios del tenant A, nunca del tenant B

### Requirement: Admin puede obtener un usuario por ID
The system SHALL allow ADMIN to retrieve a single user by UUID.

#### Scenario: Usuario existe
- **WHEN** ADMIN envía GET `/api/admin/usuarios/{id}`
- **THEN** system returns 200 con datos del usuario (sin PII en texto plano salvo autorización explícita)

#### Scenario: Usuario no existe
- **WHEN** ADMIN envía GET `/api/admin/usuarios/{id}` con UUID inexistente
- **THEN** system returns 404 Not Found

#### Scenario: Usuario de otro tenant
- **WHEN** ADMIN del tenant A solicita usuario del tenant B
- **THEN** system returns 404 Not Found (nunca filtrar datos entre tenants)

### Requirement: Admin puede actualizar usuario
The system SHALL allow ADMIN to update user fields.

#### Scenario: Actualización de campos no sensibles
- **WHEN** ADMIN envía PUT `/api/admin/usuarios/{id}` con `{nombre, apellidos, banco, regional}`
- **THEN** system returns 200 con el usuario actualizado

#### Scenario: Actualización de PII (dni, cuil, cbu, alias_cbu)
- **WHEN** ADMIN envía PUT `/api/admin/usuarios/{id}` con `{dni: "nuevo-dni"}`
- **THEN** system stores el nuevo valor cifrado con AES-256-GCM
- **AND** system returns 200

#### Scenario: Actualización de email a uno existente
- **WHEN** ADMIN actualiza email a uno ya registrado en el tenant
- **THEN** system returns 409 Conflict

### Requirement: Admin puede activar/desactivar usuario
The system SHALL allow ADMIN to toggle user's active status.

#### Scenario: Desactivar usuario
- **WHEN** ADMIN envía PATCH `/api/admin/usuarios/{id}/status` con `{activo: false}`
- **THEN** system returns 200
- **AND** el usuario queda con `activo = false`
- **AND** el usuario no puede iniciar sesión

#### Scenario: Reactivar usuario
- **WHEN** ADMIN envía PATCH `/api/admin/usuarios/{id}/status` con `{activo: true}`
- **THEN** system returns 200
- **AND** el usuario puede iniciar sesión nuevamente

### Requirement: PII cifrada no se expone en responses
The system SHALL NOT expose encrypted PII fields in API responses by default.

#### Scenario: Response de usuario no incluye PII descifrada
- **WHEN** ADMIN lista o obtiene un usuario
- **THEN** los campos `dni`, `cuil`, `cbu`, `alias_cbu` NO aparecen en la response
- **AND** `email` se muestra descifrado (necesario para identificación)

#### Scenario: No se loguea PII
- **WHEN** se registra una acción de auditoría sobre un usuario
- **THEN** los campos marcados como `[cifrado]` no aparecen en texto plano en los logs
