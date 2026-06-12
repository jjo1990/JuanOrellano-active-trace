## ADDED Requirements

### Requirement: Migration 010 creates calificacion and umbral_materia tables

The system SHALL provide an Alembic migration `010_create_calificacion_umbral.py` that creates two tables.

#### Scenario: Creates calificacion table
- **WHEN** `alembic upgrade head` is executed
- **THEN** table `calificacion` SHALL exist with columns:
  - `id` UUID PK
  - `tenant_id` UUID FK → tenant.id, NOT NULL
  - `entrada_padron_id` UUID FK → entrada_padron.id, NOT NULL
  - `materia_id` UUID FK → materia.id, NOT NULL
  - `actividad` VARCHAR(200), NOT NULL
  - `nota_numerica` NUMERIC(5,2), NULLABLE
  - `nota_textual` VARCHAR(200), NULLABLE
  - `origen` VARCHAR(20), NOT NULL
  - `importado_at` TIMESTAMPTZ, server_default=func.now(), NOT NULL
  - `created_at`, `updated_at`, `deleted_at` from BaseModelMixin

#### Scenario: Creates umbral_materia table
- **WHEN** `alembic upgrade head` is executed
- **THEN** table `umbral_materia` SHALL exist with columns:
  - `id` UUID PK
  - `tenant_id` UUID FK → tenant.id, NOT NULL
  - `asignacion_id` UUID FK → asignacion.id, NOT NULL
  - `materia_id` UUID FK → materia.id, NOT NULL
  - `umbral_pct` INTEGER, NOT NULL, server_default=60
  - `valores_aprobatorios` JSONB, NOT NULL, default=["Satisfactorio", "Supera lo esperado"]
  - `created_at`, `updated_at`, `deleted_at` from BaseModelMixin

#### Scenario: CheckConstraint on calificacion.origen
- **WHEN** the `calificacion` table is created
- **THEN** a CheckConstraint SHALL ensure `origen IN ('Importado', 'Manual')`

#### Scenario: UniqueConstraint on umbral_materia
- **WHEN** the `umbral_materia` table is created
- **THEN** a UniqueConstraint SHALL exist on `(asignacion_id, materia_id, tenant_id)`

#### Scenario: Downgrade drops both tables
- **WHEN** `alembic downgrade -1` is executed
- **THEN** tables `umbral_materia` and `calificacion` SHALL be dropped

#### Scenario: Indexes for performance
- **WHEN** the `calificacion` table is created
- **THEN** an index SHALL exist on `(entrada_padron_id, materia_id)` for efficient lookup
