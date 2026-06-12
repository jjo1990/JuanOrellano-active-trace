## ADDED Requirements

### Requirement: UmbralMateria model

The system SHALL provide a `UmbralMateria` SQLAlchemy model in `models/umbral_materia.py` with:
- `id`: UUID primary key
- `tenant_id`: UUID FK → tenant.id, NOT NULL
- `asignacion_id`: UUID FK → asignacion.id, NOT NULL
- `materia_id`: UUID FK → materia.id, NOT NULL
- `umbral_pct`: Integer, NOT NULL, server_default=60
- `valores_aprobatorios`: JSONB, NOT NULL, server_default=['Satisfactorio', 'Supera lo esperado']
- UniqueConstraint sobre `(asignacion_id, materia_id, tenant_id)`

The model SHALL inherit from `BaseModelMixin` and `Base`.

#### Scenario: Create UmbralMateria with defaults
- **WHEN** a new UmbralMateria is created with only asignacion_id and materia_id
- **THEN** `umbral_pct` SHALL default to 60 and `valores_aprobatorios` SHALL default to `["Satisfactorio", "Supera lo esperado"]`

#### Scenario: Create UmbralMateria with custom values
- **WHEN** a new UmbralMateria is created with `umbral_pct=70` and `valores_aprobatorios=["Aprobado", "Excelente"]`
- **THEN** the values SHALL be persisted as provided

#### Scenario: Unique constraint on (asignacion_id, materia_id, tenant_id)
- **WHEN** creating a second UmbralMateria with the same (asignacion_id, materia_id, tenant_id)
- **THEN** the system SHALL raise an IntegrityError

#### Scenario: Soft delete UmbralMateria
- **WHEN** an UmbralMateria is soft-deleted
- **THEN** `deleted_at` SHALL be set and the record SHALL be excluded from default queries

### Requirement: Default umbral when not configured

When no `UmbralMateria` exists for a given (asignacion_id, materia_id, tenant_id), the system SHALL use `umbral_pct=60` and `valores_aprobatorios=["Satisfactorio", "Supera lo esperado"]` as defaults (RN-03).

#### Scenario: No umbral configured returns defaults
- **WHEN** querying for a (asignacion_id, materia_id, tenant_id) without an UmbralMateria record
- **THEN** the service SHALL return default values (60, ["Satisfactorio", "Supera lo esperado"])

#### Scenario: Umbral exists returns stored values
- **WHEN** querying for a (asignacion_id, materia_id, tenant_id) with a configured UmbralMateria
- **THEN** the service SHALL return the stored umbral_pct and valores_aprobatorios
