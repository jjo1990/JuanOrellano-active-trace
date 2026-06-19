## ADDED Requirements

### Requirement: Vista admin de encuentros
El sistema SHALL permitir a COORDINADOR y ADMIN consultar transversalmente todos los encuentros del tenant (F6.5).

#### Scenario: COORDINADOR consulta todos los encuentros
- **WHEN** un COORDINADOR envía `GET /api/encuentros/admin`
- **THEN** el sistema devuelve todos los slots e instancias del tenant, incluyendo los de todos los docentes

#### Scenario: Filtrar encuentros por materia
- **WHEN** un COORDINADOR envía `GET /api/encuentros/admin?materia_id={id}`
- **THEN** el sistema devuelve solo los encuentros de esa materia

#### Scenario: Filtrar encuentros por estado de instancia
- **WHEN** un COORDINADOR envía `GET /api/encuentros/admin?estado=Programado`
- **THEN** el sistema devuelve slots cuyas instancias están en estado Programado

#### Scenario: Filtrar encuentros por rango de fechas
- **WHEN** un COORDINADOR envía `GET /api/encuentros/admin?fecha_desde=2026-03-01&fecha_hasta=2026-03-31`
- **THEN** el sistema devuelve solo los encuentros con instancias en ese rango

### Requirement: Control de acceso en vista admin
El sistema SHALL requerir el permiso `encuentros:gestionar` para acceder a la vista admin.

#### Scenario: PROFESOR intenta acceder a vista admin
- **WHEN** un PROFESOR envía `GET /api/encuentros/admin`
- **THEN** el sistema responde con 403 (PROFESOR tiene `encuentros:gestionar` para sus slots propios, pero la vista admin devuelve datos de todo el tenant — se requiere COORDINADOR)

#### Scenario: Usuario sin permiso intenta acceder
- **WHEN** un ALUMNO envía `GET /api/encuentros/admin`
- **THEN** el sistema responde con 403 Forbidden

### Requirement: Aislamiento multi-tenant en vista admin
El sistema SHALL limitar la vista admin a los encuentros del tenant del usuario autenticado.

#### Scenario: COORDINADOR de tenant A solo ve encuentros de tenant A
- **WHEN** un COORDINADOR del tenant A envía `GET /api/encuentros/admin`
- **THEN** el sistema devuelve solo encuentros del tenant A, aunque existan encuentros en tenant B
