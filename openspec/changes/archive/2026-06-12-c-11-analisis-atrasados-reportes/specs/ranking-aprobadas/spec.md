## ADDED Requirements

### Requirement: Ranking of approved activities per materia

The system SHALL provide an endpoint `GET /api/analisis/ranking/{materia_id}` that returns a ranking of students ordered by number of approved activities in descending order.

The system SHALL exclude students with zero approved activities (RN-09).

The system SHALL compute "approved" using `_es_aprobado()` logic: numeric nota >= umbral_pct, or textual nota in valores_aprobatorios. Defaults apply when no UmbralMateria is configured.

The response SHALL include per student: EntradaPadron data, cantidad total de actividades de la materia, cantidad de aprobadas, and porcentaje de aprobación.

#### Scenario: Ranking with mixed approvals

- **WHEN** materia X has 4 activities, umbral_pct=60, and:
  - Student A has 3 approved, 1 not approved
  - Student B has 2 approved, 2 not approved
  - Student C has 4 approved
  - Student D has 0 approved
- **THEN** the ranking returns [C (4), A (3), B (2)] in descending order. Student D is excluded.

#### Scenario: All students with at least one approved

- **WHEN** every student in the materia has >=1 approved activity
- **THEN** all students appear in the ranking

#### Scenario: No student has any approved activity

- **WHEN** no student in the materia has any approved activity
- **THEN** the endpoint returns an empty ranking list with status_info

#### Scenario: Ranking with default umbral when none configured

- **WHEN** no UmbralMateria exists and default umbral_pct=60 applies
- **THEN** a nota_numerica=60 counts as approved and nota_numerica=59 counts as not approved

#### Scenario: Ranking with textual notas

- **WHEN** student has nota_textual="Satisfactorio" and valores_aprobatorios=["Satisfactorio", "Supera lo esperado"]
- **THEN** that activity counts as approved

#### Scenario: Ranking response schema

- **WHEN** the ranking is computed
- **THEN** the response SHALL contain `materia_id`, `total_alumnos`, `ranking: list[RankingEntryDTO]` with fields `entrada_padron_id`, `nombre`, `apellidos`, `email`, `comision`, `regional`, `total_actividades`, `aprobadas`, `porcentaje`

#### Scenario: Tenant isolation

- **WHEN** tenant A requests the ranking and tenant B has data for the same materia
- **THEN** only tenant A's data is used
