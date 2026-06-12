## ADDED Requirements

### Requirement: VersionPadron como entidad de versionado

El sistema SHALL modelar `VersionPadron` como la entidad que representa una versión del padrón de alumnos para una materia y cohorte específicas. Cada import exitoso de padrón SHALL crear una nueva `VersionPadron`. Solo una versión SHALL estar activa por par (materia_id, cohorte_id) en un mismo tenant.

#### Scenario: Creación de una VersionPadron

- **GIVEN** una materia y una cohorte existentes en el tenant
- **WHEN** se crea una `VersionPadron` para esa materia y cohorte
- **THEN** la versión se guarda con `activa = True`
- **AND** se registra `cargado_por` con el UUID del usuario que realizó la carga
- **AND** el campo `cargado_at` se establece automáticamente

#### Scenario: Activar nueva versión desactiva la anterior

- **GIVEN** una `VersionPadron` activa (V1) para (materia M, cohorte C)
- **WHEN** se crea una nueva `VersionPadron` (V2) para (materia M, cohorte C) en el mismo tenant
- **THEN** V1.activa pasa a `False`
- **AND** V2.activa se establece a `True`
- **AND** V1 no se elimina (soft delete no se aplica)

#### Scenario: Aislamiento multi-tenant en versionado

- **GIVEN** dos tenants A y B, cada uno con (materia M, cohorte C)
- **AND** una VersionPadron activa en tenant A
- **WHEN** se activa una nueva VersionPadron en tenant B para (materia M, cohorte C)
- **THEN** la VersionPadron del tenant A permanece activa
- **AND** solo la del tenant B se desactiva al activar su reemplazo

#### Scenario: Soft delete de VersionPadron

- **GIVEN** una VersionPadron existente
- **WHEN** se ejecuta soft delete sobre ella
- **THEN** el campo `deleted_at` se establece al momento actual
- **AND** las EntradaPadron asociadas no se eliminan en cascada
