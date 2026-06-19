## ADDED Requirements

### Requirement: ABM de plus salarial
El sistema SHALL permitir a FINANZAS crear, consultar, modificar y eliminar (soft delete) registros de `SalarioPlus`. Cada registro define un monto adicional para una combinación `(grupo, rol)` con vigencia `desde`/`hasta`.

#### Scenario: Crear plus salarial
- **WHEN** FINANZAS envía `POST /api/salarios/plus` con `grupo=PROG`, `rol=PROFESOR`, `monto=15000.00`, `descripcion="Plus Programación"`, `desde=2026-01-01`
- **THEN** el sistema crea el registro y retorna 201.

#### Scenario: Modificar monto de plus
- **WHEN** FINANZAS envía `PUT /api/salarios/plus/{id}` con `monto=18000.00`
- **THEN** el sistema actualiza solo el monto, manteniendo el resto de campos, y retorna 200.

### Requirement: Unicidad de plus vigente por grupo y rol
El sistema SHALL garantizar que no existan dos entradas de `SalarioPlus` con el mismo `(grupo, rol)` cuyas vigencias se solapen.

#### Scenario: Solapamiento rechazado
- **WHEN** existe `SalarioPlus(grupo=PROG, rol=PROFESOR, desde=2026-01-01, hasta=null)` y se intenta crear otro con `(PROG, PROFESOR, desde=2026-06-01)`
- **THEN** el sistema retorna 409.

### Requirement: Listado de grilla de plus
El sistema SHALL permitir listar todas las entradas de `SalarioPlus` del tenant, con filtro opcional por grupo y rol.

#### Scenario: Listado con filtro de grupo
- **WHEN** se solicita `GET /api/salarios/plus?grupo=PROG`
- **THEN** el sistema retorna solo los plus del grupo PROG, ordenados por rol y vigencia.

### Requirement: Plus aplicable a cálculo de liquidación
El sistema SHALL exponer un endpoint que retorne el plus vigente para una combinación `(grupo, rol, fecha)` específica.

#### Scenario: Plus vigente encontrado
- **WHEN** se consulta `GET /api/salarios/plus/vigente?grupo=PROG&rol=PROFESOR&fecha=2026-06-01`
- **THEN** el sistema retorna 200 con el monto aplicable.

#### Scenario: Sin plus vigente
- **WHEN** no existe entrada para `(grupo, rol)` en la fecha consultada
- **THEN** el sistema retorna 200 con `monto=0`, indicando que no aplica plus.
