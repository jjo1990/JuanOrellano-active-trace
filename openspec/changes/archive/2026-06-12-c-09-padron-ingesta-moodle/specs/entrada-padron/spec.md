## ADDED Requirements

### Requirement: EntradaPadron como registro individual de padrón

El sistema SHALL modelar `EntradaPadron` como el registro individual de un alumno dentro de una versión de padrón. Cada fila del archivo importado SHALL corresponder a una `EntradaPadron`. Los datos se desnormalizan para preservar el histórico aunque el usuario se modifique después.

#### Scenario: Entrada con datos completos

- **GIVEN** una VersionPadron existente
- **WHEN** se crea una EntradaPadron con nombre, apellidos, email, comisión y regional
- **THEN** la entrada se guarda asociada a esa versión mediante `version_id`
- **AND** el email se almacena cifrado

#### Scenario: Entrada sin usuario_id (alumno sin cuenta)

- **GIVEN** un alumno que no tiene cuenta de usuario en el sistema
- **WHEN** se crea una EntradaPadron para ese alumno
- **THEN** `usuario_id` es `NULL`
- **AND** los datos desnormalizados (nombre, apellidos, email) se almacenan igualmente

#### Scenario: Entrada con usuario_id existente

- **GIVEN** un alumno con cuenta de usuario (rol ALUMNO) en el mismo tenant
- **WHEN** se crea una EntradaPadron para ese alumno
- **THEN** `usuario_id` se vincula al UUID del usuario existente
- **AND** se verifica que el usuario pertenece al mismo tenant

#### Scenario: Aislamiento multi-tenant en EntradaPadron

- **GIVEN** una EntradaPadron perteneciente al tenant A
- **WHEN** un repository del tenant B ejecuta `list()` sobre EntradaPadron
- **THEN** la entrada del tenant A no aparece en los resultados

#### Scenario: Soft delete de EntradaPadron

- **GIVEN** una EntradaPadron existente
- **WHEN** se ejecuta soft delete
- **THEN** `deleted_at` se establece al momento actual
- **AND** el registro continúa existiendo en la base de datos
