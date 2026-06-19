## ADDED Requirements

### Requirement: ABM de salarios base por rol
El sistema SHALL permitir al usuario FINANZAS gestionar la tabla de salarios base: crear, editar y desactivar registros con rol, monto y vigencia desde/hasta.

#### Scenario: Crear salario base
- **WHEN** el usuario completa el formulario con rol "PROFESOR", monto 150000, vigencia desde "2026-03-01" y guarda
- **THEN** el sistema crea el registro y lo agrega a la tabla de salarios base.

#### Scenario: Editar salario base existente
- **WHEN** el usuario modifica el monto de un registro existente y guarda
- **THEN** el sistema actualiza el monto manteniendo la vigencia y rol.

#### Scenario: Desactivar salario base
- **WHEN** el usuario desactiva un registro de salario base
- **THEN** el sistema marca el registro como inactivo. No se elimina físicamente.

### Requirement: ABM de plus
El sistema SHALL permitir gestionar la tabla de plus: crear, editar y desactivar registros con clave, rol, descripción, monto o porcentaje, y vigencia desde/hasta.

#### Scenario: Crear plus por monto fijo
- **WHEN** el usuario crea un plus con clave "ANTIGUEDAD", rol "PROFESOR", monto fijo 10000, vigencia desde "2026-03-01"
- **THEN** el sistema crea el registro y lo muestra en la tabla de plus.

#### Scenario: Crear plus por porcentaje
- **WHEN** el usuario crea un plus con clave "EXTRA", rol "TUTOR", porcentaje 15%, vigencia desde "2026-03-01"
- **THEN** el sistema crea el registro indicando que es un plus porcentual.

#### Scenario: Vigencia de plus solapada detectada
- **WHEN** el usuario intenta crear un plus con la misma clave y rol cuya vigencia se solapa con uno existente
- **THEN** el sistema muestra un error de solapamiento de vigencias.
