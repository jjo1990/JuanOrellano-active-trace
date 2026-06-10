## ADDED Requirements

### Requirement: ADMIN puede crear una cohorte
El sistema SHALL permitir a un usuario con permiso `estructura:gestionar` crear una nueva cohorte vinculada a una carrera existente y activa.

#### Scenario: Creación exitosa en carrera activa
- **WHEN** un ADMIN envía `POST /api/admin/cohortes` con `{carrera_id: <uuid>, nombre: "MAR-2026", anio: 2026, vig_desde: "2026-03-01", estado: true}`
- **THEN** el sistema retorna `201` con la cohorte creada

#### Scenario: Carrera inexistente
- **WHEN** un ADMIN crea una cohorte referenciando un `carrera_id` que no existe
- **THEN** el sistema retorna `404 Not Found`

#### Scenario: Carrera inactiva no permite cohortes activas
- **WHEN** un ADMIN intenta crear una cohorte con `estado: true` vinculada a una carrera inactiva
- **THEN** el sistema retorna `409 Conflict` con mensaje "No se puede crear una cohorte activa para una carrera inactiva"

#### Scenario: Nombre duplicado en misma carrera y tenant
- **WHEN** un ADMIN crea una cohorte con un `nombre` que ya existe para la misma `carrera_id` en el mismo tenant
- **THEN** el sistema retorna `409 Conflict`

#### Scenario: Nombre duplicado en distinta carrera (permitido)
- **WHEN** un ADMIN crea una cohorte con `nombre: "MAR-2026"` para una carrera distinta
- **THEN** el sistema retorna `201 Created` (el unique constraint es por `(tenant_id, carrera_id, nombre)`)

### Requirement: ADMIN puede listar cohortes
El sistema SHALL permitir listar todas las cohortes del tenant activo.

#### Scenario: Listado exitoso
- **WHEN** un ADMIN envía `GET /api/admin/cohortes`
- **THEN** el sistema retorna `200` con un array de cohortes del tenant

### Requirement: ADMIN puede actualizar una cohorte
El sistema SHALL permitir modificar nombre, año, vigencia y estado de una cohorte.

#### Scenario: Actualización exitosa
- **WHEN** un ADMIN envía `PUT /api/admin/cohortes/{id}` con `{nombre: "AGO-2026", vig_hasta: "2026-08-31"}`
- **THEN** el sistema retorna `200` con la cohorte actualizada

#### Scenario: Reactivar cohorte de carrera inactiva
- **WHEN** un ADMIN intenta cambiar `estado: true` en una cohorte cuya carrera está inactiva
- **THEN** el sistema retorna `409 Conflict`
