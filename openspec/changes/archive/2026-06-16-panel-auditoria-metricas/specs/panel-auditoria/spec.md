## ADDED Requirements

### Requirement: Panel de interacciones con 4 vistas agregadas
El sistema SHALL exponer un panel de métricas con acciones por día, estado de comunicaciones, interacciones por docente×materia y log de últimas acciones (F9.1, HU-37).

#### Scenario: ADMIN consulta panel completo
- **WHEN** un ADMIN envía `GET /api/auditoria/panel`
- **THEN** devuelve: acciones_por_dia (count agrupado por fecha), estado_comunicaciones (count por docente y estado), interacciones_docente_materia (count por docente, materia y tipo de acción), ultimas_acciones (últimos 200 registros)

#### Scenario: Filtrar panel por rango de fechas
- **WHEN** `GET /api/auditoria/panel?fecha_desde=2026-03-01&fecha_hasta=2026-03-31`
- **THEN** todas las secciones se limitan a ese rango

#### Scenario: COORDINADOR con scope propio
- **WHEN** un COORDINADOR consulta el panel
- **THEN** solo ve datos de materias donde tiene asignación vigente (scope propio)

#### Scenario: Límite configurable
- **WHEN** `GET /api/auditoria/panel?limite=50`
- **THEN** ultimas_acciones devuelve máximo 50 registros

### Requirement: Control de acceso al panel
El sistema SHALL requerir `auditoria:ver` para acceder al panel.

#### Scenario: Usuario sin permiso
- **WHEN** un PROFESOR envía `GET /api/auditoria/panel`
- **THEN** 403
