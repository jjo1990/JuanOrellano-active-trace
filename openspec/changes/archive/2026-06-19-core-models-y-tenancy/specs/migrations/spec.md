## ADDED Requirements

### Requirement: Migration 001 — tabla tenant

El sistema SHALL tener una migración Alembic (001) que cree la tabla `tenant` en la base de datos. La migración SHALL ser la primera del proyecto y SHALL ejecutarse sobre el esquema público.

#### Scenario: Tabla tenant se crea correctamente

- **WHEN** se ejecuta `alembic upgrade head`
- **THEN** la tabla `tenant` existe en la base de datos
- **AND** contiene las columnas: `id` (UUID, PK), `nombre` (VARCHAR, NOT NULL), `slug` (VARCHAR, NOT NULL, UNIQUE), `config` (JSONB, NOT NULL, default '{}'), `estado` (VARCHAR, NOT NULL, default 'activo'), `created_at` (TIMESTAMPTZ, NOT NULL), `updated_at` (TIMESTAMPTZ, NOT NULL), `deleted_at` (TIMESTAMPTZ, nullable)

#### Scenario: Índices de tenant

- **WHEN** se ejecuta `alembic upgrade head`
- **THEN** existe un índice único sobre la columna `slug`
- **AND** existe un índice sobre la columna `estado`

#### Scenario: Rollback funciona

- **GIVEN** la migración 001 aplicada
- **WHEN** se ejecuta `alembic downgrade -1`
- **THEN** la tabla `tenant` se elimina
- **AND** la base de datos queda en el estado previo a la migración

### Requirement: Migration usa engine async

La migración SHALL utilizar el engine async configurado en `alembic/env.py` (heredado de C-01).

#### Scenario: Configuración async

- **WHEN** se ejecuta `alembic upgrade head`
- **THEN** la migración utiliza el motor async de SQLAlchemy configurado en el entorno de Alembic
- **AND** no se requiere configuración adicional para el driver async
