## ADDED Requirements

### Requirement: Listado de usuarios del tenant
El sistema SHALL mostrar una tabla con todos los usuarios del tenant: nombre, email, roles asignados, regional, estado (activo/inactivo) y acciones.

#### Scenario: Ver lista de usuarios
- **WHEN** el usuario ADMIN accede a la vista de usuarios
- **THEN** el sistema muestra una tabla con todos los usuarios del tenant, paginada, con columnas: nombre, email, roles, regional, estado, acciones.

#### Scenario: Filtrar por rol
- **WHEN** el usuario selecciona un rol en el filtro (ej. "PROFESOR")
- **THEN** el sistema muestra solo los usuarios que tienen ese rol asignado.

### Requirement: Alta de usuario
El sistema SHALL permitir al ADMIN dar de alta un nuevo usuario con: nombre, email, identificación fiscal, roles, datos bancarios (banco, CBU/alias), regional, y modalidad de facturación.

#### Scenario: Crear usuario profesor
- **WHEN** el usuario completa el formulario con nombre "Juan Pérez", email "juan@inst.edu", rol "PROFESOR", banco "Santander", CBU "0000000000000000000000", regional "Capital" y guarda
- **THEN** el sistema crea el usuario, envía credenciales iniciales al email y lo agrega a la tabla.

#### Scenario: Crear usuario que factura
- **WHEN** el usuario marca "Factura" como modalidad de cobro al crear un usuario
- **THEN** el sistema registra al usuario como docente que factura. No aparecerá en la liquidación general.

### Requirement: Edición de usuario
El sistema SHALL permitir editar los datos de un usuario existente: nombre, email, roles, datos bancarios, regional, modalidad de facturación, estado de actividad.

#### Scenario: Cambiar rol de usuario
- **WHEN** el usuario agrega el rol "COORDINADOR" a un usuario existente y guarda
- **THEN** el sistema actualiza los roles del usuario. El usuario ahora tiene permisos de COORDINADOR.

#### Scenario: Activar/desactivar usuario
- **WHEN** el usuario cambia el estado de un usuario de "Activo" a "Inactivo"
- **THEN** el sistema desactiva al usuario. No puede iniciar sesión hasta ser reactivado.

### Requirement: Campos bancarios cifrados en reposo
Los datos bancarios (CBU, alias) SHALL mostrarse enmascarados por defecto en la interfaz, con opción de revelar bajo confirmación.

#### Scenario: Ver CBU enmascarado
- **WHEN** el usuario ve la ficha de un docente con CBU registrado
- **THEN** el sistema muestra el CBU enmascarado (últimos 4 dígitos visibles) con un botón "Revelar".

#### Scenario: Revelar CBU completo
- **WHEN** el usuario hace clic en "Revelar" y confirma
- **THEN** el sistema muestra el CBU completo por 30 segundos y luego lo vuelve a enmascarar.
