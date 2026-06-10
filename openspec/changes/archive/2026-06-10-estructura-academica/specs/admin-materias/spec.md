## ADDED Requirements

### Requirement: ADMIN puede crear una materia
El sistema SHALL permitir a un usuario con permiso `estructura:gestionar` crear una nueva materia en el catálogo del tenant.

#### Scenario: Creación exitosa
- **WHEN** un ADMIN envía `POST /api/admin/materias` con `{codigo: "PROG_I", nombre: "Programación I", estado: true}`
- **THEN** el sistema retorna `201` con la materia creada

#### Scenario: Código duplicado en el mismo tenant
- **WHEN** un ADMIN crea una materia con un `codigo` que ya existe en su tenant
- **THEN** el sistema retorna `409 Conflict`

#### Scenario: Código duplicado en otro tenant (permitido)
- **WHEN** un ADMIN del tenant A crea una materia con `codigo` que ya existe en el tenant B
- **THEN** el sistema retorna `201 Created`

### Requirement: ADMIN puede listar materias
El sistema SHALL permitir listar todas las materias del catálogo del tenant activo.

#### Scenario: Listado exitoso
- **WHEN** un ADMIN envía `GET /api/admin/materias`
- **THEN** el sistema retorna `200` con un array de materias del tenant

### Requirement: ADMIN puede actualizar una materia
El sistema SHALL permitir modificar nombre y estado de una materia.

#### Scenario: Actualización exitosa
- **WHEN** un ADMIN envía `PUT /api/admin/materias/{id}` con `{nombre: "Programación I (Actualizado)", estado: false}`
- **THEN** el sistema retorna `200` con la materia actualizada

### Requirement: Aislamiento multi-tenant en materias
El sistema SHALL garantizar que las materias de un tenant no sean accesibles desde otro tenant.

#### Scenario: Usuario de tenant A no puede modificar materia de tenant B
- **WHEN** un ADMIN del tenant A envía `PUT /api/admin/materias/{id}` con un `{id}` de una materia del tenant B
- **THEN** el sistema retorna `404 Not Found` (el repository filtra por tenant_id, no encuentra el recurso)
