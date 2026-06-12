## ADDED Requirements

### Requirement: Migration 009 crea tablas version_padron y entrada_padron

El sistema SHALL incluir una migración Alembic (009) que cree las tablas `version_padron` y `entrada_padron` con sus columnas, FK, índices y constraints según el modelo de datos. La migración SHALL ser reversible.

#### Scenario: Upgrade crea ambas tablas

- **GIVEN** la base de datos en migración 008
- **WHEN** se ejecuta `alembic upgrade head`
- **THEN** se crea la tabla `version_padron` con columnas: id (UUID PK), tenant_id (FK), materia_id (FK), cohorte_id (FK), cargado_por (FK), cargado_at (timestamp), activa (boolean), created_at, updated_at, deleted_at
- **AND** se crea la tabla `entrada_padron` con columnas: id (UUID PK), version_id (FK), tenant_id (FK), usuario_id (FK nullable), nombre, apellidos, email (String), comision, regional, created_at, updated_at, deleted_at
- **AND** se crea un índice único parcial para garantizar una sola versión activa por (materia_id, cohorte_id, tenant_id)
- **AND** se verifican las FK: version_padron.materia_id → materia.id, version_padron.cohorte_id → cohorte.id, version_padron.cargado_por → user.id, entrada_padron.version_id → version_padron.id, entrada_padron.usuario_id → user.id

#### Scenario: Downgrade revierte ambas tablas

- **GIVEN** la base de datos en migración 009
- **WHEN** se ejecuta `alembic downgrade -1`
- **THEN** se elimina la tabla `entrada_padron`
- **AND** se elimina la tabla `version_padron`
