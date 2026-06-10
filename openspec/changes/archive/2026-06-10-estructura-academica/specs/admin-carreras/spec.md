## ADDED Requirements

### Requirement: ADMIN puede crear una carrera
El sistema SHALL permitir a un usuario con permiso `estructura:gestionar` crear una nueva carrera en su tenant.

#### Scenario: Creación exitosa
- **WHEN** un ADMIN envía `POST /api/admin/carreras` con `{codigo: "TUPAD", nombre: "Tecnicatura Universitaria en Programación", estado: true}`
- **THEN** el sistema retorna `201` con la carrera creada, incluyendo `id`, `tenant_id`, `codigo`, `nombre`, `estado`, `created_at`, `updated_at`

#### Scenario: Código duplicado en el mismo tenant
- **WHEN** un ADMIN crea una carrera con un `codigo` que ya existe en su tenant
- **THEN** el sistema retorna `409 Conflict`

#### Scenario: Código duplicado en otro tenant (permitido)
- **WHEN** un ADMIN del tenant A crea una carrera con `codigo` que ya existe en el tenant B
- **THEN** el sistema retorna `201 Created` (el aislamiento multi-tenant permite códigos iguales entre tenants)

#### Scenario: Sin permiso `estructura:gestionar`
- **WHEN** un usuario sin el permiso `estructura:gestionar` envía `POST /api/admin/carreras`
- **THEN** el sistema retorna `403 Forbidden`

### Requirement: ADMIN puede listar carreras
El sistema SHALL permitir listar todas las carreras del tenant activo.

#### Scenario: Listado exitoso
- **WHEN** un ADMIN envía `GET /api/admin/carreras`
- **THEN** el sistema retorna `200` con un array de carreras del tenant (vacío si no hay ninguna)

### Requirement: ADMIN puede actualizar una carrera
El sistema SHALL permitir modificar nombre y estado de una carrera.

#### Scenario: Actualización exitosa
- **WHEN** un ADMIN envía `PUT /api/admin/carreras/{id}` con `{nombre: "Nuevo nombre", estado: false}`
- **THEN** el sistema retorna `200` con la carrera actualizada

#### Scenario: Carrera inexistente
- **WHEN** un ADMIN envía `PUT /api/admin/carreras/{id}` con un `{id}` que no existe
- **THEN** el sistema retorna `404 Not Found`

#### Scenario: Inactivar carrera con cohortes activas
- **WHEN** un ADMIN inactiva una carrera que tiene cohortes activas (vig_hasta IS NULL)
- **THEN** el sistema retorna `409 Conflict` con mensaje indicando que debe cerrar las cohortes primero
