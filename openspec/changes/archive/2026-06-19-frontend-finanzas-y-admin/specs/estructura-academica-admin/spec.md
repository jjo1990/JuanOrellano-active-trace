## ADDED Requirements

### Requirement: ABM de carreras
El sistema SHALL permitir al ADMIN crear, editar y cambiar el estado (activa/inactiva) de carreras del tenant.

#### Scenario: Crear carrera
- **WHEN** el usuario completa el formulario con código "ING-INF" y nombre "Ingeniería Informática" y guarda
- **THEN** el sistema crea la carrera y la muestra en la tabla con estado "Activa".

#### Scenario: Editar carrera
- **WHEN** el usuario modifica el nombre de una carrera existente y guarda
- **THEN** el sistema actualiza el nombre manteniendo el código.

#### Scenario: Desactivar carrera
- **WHEN** el usuario desactiva una carrera activa
- **THEN** el sistema cambia el estado a "Inactiva". La carrera sigue visible en la tabla pero no puede asociarse a nuevas cohortes.

#### Scenario: Reactivar carrera
- **WHEN** el usuario activa una carrera inactiva
- **THEN** el sistema cambia el estado a "Activa".

### Requirement: ABM de cohortes
El sistema SHALL permitir al ADMIN crear, editar y cambiar el estado de cohortes, con nombre, año de inicio, fechas de vigencia desde/hasta.

#### Scenario: Crear cohorte
- **WHEN** el usuario completa el formulario con nombre "MAR-2026", año inicio 2026, vigencia desde "2026-03-01" hasta "2026-07-31" y guarda
- **THEN** el sistema crea la cohorte y la muestra en la tabla.

#### Scenario: Cerrar cohorte
- **WHEN** el usuario cambia una cohorte activa a estado inactiva
- **THEN** el sistema marca la cohorte como inactiva. No se elimina.

### Requirement: Validación de vigencias de cohorte
El sistema SHALL validar que la fecha desde sea anterior a la fecha hasta al crear o editar una cohorte.

#### Scenario: Vigencia inválida
- **WHEN** el usuario ingresa fecha desde "2026-07-01" y fecha hasta "2026-03-01"
- **THEN** el sistema muestra un error "La fecha desde debe ser anterior a la fecha hasta".
