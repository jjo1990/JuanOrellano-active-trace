## ADDED Requirements

### Requirement: ABM de salario base por rol
El sistema SHALL permitir a FINANZAS crear, consultar, modificar y eliminar (soft delete) registros de `SalarioBase`. Cada registro define un monto base para un rol, con vigencia `desde`/`hasta`.

#### Scenario: Crear salario base
- **WHEN** FINANZAS envía `POST /api/salarios/base` con `rol=PROFESOR`, `monto=80000.00`, `desde=2026-01-01`
- **THEN** el sistema crea el registro con `tenant_id` de la sesión y retorna 201 con el recurso creado.

#### Scenario: Crear salario base sin permiso
- **WHEN** un usuario sin permiso `liquidaciones:configurar-salarios` intenta crear un salario base
- **THEN** el sistema retorna 403.

#### Scenario: Vigencia solapada rechazada
- **WHEN** ya existe `SalarioBase(rol=PROFESOR, desde=2026-01-01, hasta=null)` y se intenta crear otro con `rol=PROFESOR, desde=2026-03-01`
- **THEN** el sistema retorna 409 indicando que ya existe una entrada vigente para ese rol en ese período.

### Requirement: Consulta de salario base vigente
El sistema SHALL permitir consultar el `SalarioBase` vigente para un rol en una fecha determinada.

#### Scenario: Consulta con entrada vigente
- **WHEN** se consulta `GET /api/salarios/base?rol=PROFESOR&fecha=2026-06-01` y existe una entrada con `desde <= 2026-06-01 <= hasta`
- **THEN** el sistema retorna 200 con el monto vigente.

#### Scenario: Consulta sin entrada vigente
- **WHEN** se consulta para un rol sin entrada vigente en la fecha dada
- **THEN** el sistema retorna 404 con mensaje descriptivo.

### Requirement: Listado de grilla salarial base
El sistema SHALL permitir listar todas las entradas de `SalarioBase` del tenant, con filtro opcional por rol y estado de vigencia.

#### Scenario: Listado completo
- **WHEN** FINANZAS solicita `GET /api/salarios/base`
- **THEN** el sistema retorna 200 con array de todas las entradas del tenant, ordenadas por rol y `desde` descendente.

#### Scenario: Filtro por rol
- **WHEN** se solicita `GET /api/salarios/base?rol=TUTOR`
- **THEN** el sistema retorna solo las entradas del rol TUTOR.
