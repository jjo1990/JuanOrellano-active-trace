## ADDED Requirements

### Requirement: Permiso padron:importar

El sistema SHALL registrar el permiso `padron:importar` en la matriz de permisos. Este permiso SHALL ser asignable a los roles PROFESOR (para sus materias asignadas) y COORDINADOR (para cualquier materia del tenant).

#### Scenario: PROFESOR con padron:importar puede importar

- **GIVEN** un usuario con rol PROFESOR y permiso `padron:importar`
- **WHEN** intenta importar un padrón para una materia que tiene asignada
- **THEN** la operación es autorizada

#### Scenario: COORDINADOR con padron:importar puede importar cualquier materia

- **GIVEN** un usuario con rol COORDINADOR y permiso `padron:importar`
- **WHEN** intenta importar un padrón para cualquier materia del tenant
- **THEN** la operación es autorizada

#### Scenario: Usuario sin padron:importar recibe 403

- **GIVEN** un usuario autenticado sin permiso `padron:importar`
- **WHEN** intenta importar un padrón
- **THEN** el sistema retorna 403 Forbidden
