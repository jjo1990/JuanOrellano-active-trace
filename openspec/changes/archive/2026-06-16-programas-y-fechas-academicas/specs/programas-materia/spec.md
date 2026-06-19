## ADDED Requirements

### Requirement: Subir programa de materia
El sistema SHALL permitir a COORDINADOR/ADMIN asociar un programa oficial a una materia × carrera × cohorte (F5.3, HU-23).

#### Scenario: Subir programa exitoso
- **WHEN** un COORDINADOR envía `POST /api/programas` con materia_id, carrera_id, cohorte_id, titulo, referencia_archivo
- **THEN** el sistema crea el registro con cargado_at automático

#### Scenario: Programa sin archivo
- **WHEN** se envía sin referencia_archivo
- **THEN** el sistema rechaza con 422

### Requirement: Listar programas con filtros
El sistema SHALL listar programas filtrables por materia, carrera y cohorte.

#### Scenario: Filtrar por materia
- **WHEN** `GET /api/programas?materia_id=X`
- **THEN** devuelve solo programas de esa materia

### Requirement: Reemplazar programa
El sistema SHALL permitir actualizar título y referencia_archivo de un programa existente (HU-23).

#### Scenario: Reemplazar archivo
- **WHEN** COORDINADOR envía `PUT /api/programas/{id}` con nuevo referencia_archivo
- **THEN** actualiza el registro

### Requirement: Soft delete programa
El sistema SHALL implementar soft delete para programas.

### Requirement: Aislamiento multi-tenant
El sistema SHALL aislar programas por tenant.
