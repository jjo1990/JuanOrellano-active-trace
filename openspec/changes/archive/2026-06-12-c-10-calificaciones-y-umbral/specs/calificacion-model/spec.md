## ADDED Requirements

### Requirement: Calificacion model

The system SHALL provide a `Calificacion` SQLAlchemy model in `models/calificacion.py` with:
- `id`: UUID primary key
- `tenant_id`: UUID FK → tenant.id, NOT NULL
- `entrada_padron_id`: UUID FK → entrada_padron.id, NOT NULL
- `materia_id`: UUID FK → materia.id, NOT NULL
- `actividad`: String(200), NOT NULL — nombre de la actividad evaluable
- `nota_numerica`: Numeric(5,2), NULLABLE
- `nota_textual`: String(200), NULLABLE
- `origen`: String(20), NOT NULL — con CheckConstraint `IN ('Importado', 'Manual')`
- `importado_at`: TIMESTAMP(timezone=True), server_default=func.now(), NOT NULL

The model SHALL inherit from `BaseModelMixin` and `Base` (soft delete, timestamps, tenant_id from mixin).

The `aprobado` field SHALL NOT be stored in the database — it SHALL be computed dynamically in the service layer.

#### Scenario: Create Calificacion with nota_numerica
- **WHEN** a new Calificacion is created with `nota_numerica=85` and `nota_textual=None`
- **THEN** the record SHALL be persisted with `nota_numerica=85` and `nota_textual=None`

#### Scenario: Create Calificacion with nota_textual
- **WHEN** a new Calificacion is created with `nota_textual="Satisfactorio"` and `nota_numerica=None`
- **THEN** the record SHALL be persisted with `nota_textual="Satisfactorio"` and `nota_numerica=None`

#### Scenario: Create Calificacion with both notas
- **WHEN** a new Calificacion is created with both `nota_numerica=70` and `nota_textual="Bueno"`
- **THEN** the record SHALL be persisted with both values

#### Scenario: Create Calificacion with origen Importado
- **WHEN** a Calificacion is created with `origen="Importado"`
- **THEN** the CheckConstraint SHALL allow the value

#### Scenario: Create Calificacion with origen Manual
- **WHEN** a Calificacion is created with `origen="Manual"`
- **THEN** the CheckConstraint SHALL allow the value

#### Scenario: Create Calificacion with invalid origen
- **WHEN** a Calificacion is created with `origen="Invalido"`
- **THEN** the CheckConstraint SHALL reject the value

#### Scenario: Soft delete Calificacion
- **WHEN** a Calificacion is soft-deleted
- **THEN** `deleted_at` SHALL be set and the record SHALL be excluded from default queries

### Requirement: Computed aprobado derivation

The system SHALL compute `aprobado` in `CalificacionesService._es_aprobado()` following RN-01, RN-02, RN-03:
- If `nota_numerica` exists → `nota_numerica >= umbral_materia.umbral_pct` (default 60 if no umbral configured)
- If only `nota_textual` exists → `nota_textual IN umbral_materia.valores_aprobatorios` (default `["Satisfactorio", "Supera lo esperado"]`)
- If neither exists → `False`

#### Scenario: Numeric nota above threshold
- **WHEN** `nota_numerica=75` and `umbral_pct=60`
- **THEN** `_es_aprobado()` SHALL return `True`

#### Scenario: Numeric nota below threshold
- **WHEN** `nota_numerica=55` and `umbral_pct=60`
- **THEN** `_es_aprobado()` SHALL return `False`

#### Scenario: Textual nota Satisfactorio
- **WHEN** `nota_textual="Satisfactorio"` and `valores_aprobatorios=["Satisfactorio", "Supera lo esperado"]`
- **THEN** `_es_aprobado()` SHALL return `True`

#### Scenario: Textual nota NOT in approved values
- **WHEN** `nota_textual="Regular"` and `valores_aprobatorios=["Satisfactorio", "Supera lo esperado"]`
- **THEN** `_es_aprobado()` SHALL return `False`

#### Scenario: No umbral configured uses defaults
- **WHEN** `nota_numerica=60` and `umbral=None`
- **THEN** `_es_aprobado()` SHALL return `True` (default 60%)

#### Scenario: No nota at all
- **WHEN** `nota_numerica=None` and `nota_textual=None`
- **THEN** `_es_aprobado()` SHALL return `False`
