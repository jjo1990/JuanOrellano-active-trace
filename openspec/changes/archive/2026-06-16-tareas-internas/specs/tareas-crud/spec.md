## ADDED Requirements

### Requirement: Crear tarea
El sistema SHALL permitir a cualquier usuario autenticado crear una tarea asignada a otro docente.

#### Scenario: COORDINADOR crea tarea para PROFESOR
- **WHEN** un COORDINADOR envía `POST /api/tareas` con materia_id, asignado_a, descripcion
- **THEN** el sistema crea la tarea con estado Pendiente y asignado_por = COORDINADOR

#### Scenario: Crear tarea sin materia (institucional)
- **WHEN** un COORDINADOR crea tarea sin materia_id
- **THEN** el sistema acepta (materia_id nullable para tareas institucionales)

### Requirement: Mis tareas asignadas
El sistema SHALL mostrar al usuario las tareas que le fueron asignadas, con filtros (F8.1, HU-34).

#### Scenario: PROFESOR ve sus tareas
- **WHEN** un PROFESOR envía `GET /api/tareas/mis-tareas`
- **THEN** el sistema devuelve solo tareas donde asignado_a = user_id, con último comentario

#### Scenario: Filtrar mis tareas por estado
- **WHEN** un PROFESOR envía `GET /api/tareas/mis-tareas?estado=Pendiente`
- **THEN** solo devuelve tareas Pendientes

#### Scenario: Filtrar mis tareas por materia
- **WHEN** un PROFESOR envía `GET /api/tareas/mis-tareas?materia_id=X`
- **THEN** solo devuelve tareas de esa materia

### Requirement: Cambiar estado de tarea
El sistema SHALL permitir cambiar el estado de una tarea (F8.3). El asignado puede mover a En progreso o Resuelta. COORDINADOR puede cualquier transición.

#### Scenario: PROFESOR inicia tarea
- **WHEN** el PROFESOR asignado envía `PUT /api/tareas/{id}/estado` con estado=En progreso
- **THEN** el sistema actualiza el estado

#### Scenario: PROFESOR resuelve tarea
- **WHEN** el PROFESOR asignado envía estado=Resuelta
- **THEN** el sistema actualiza

#### Scenario: Cancelar tarea desde cualquier estado
- **WHEN** un COORDINADOR envía estado=Cancelada
- **THEN** el sistema acepta la transición

### Requirement: Delegar tarea
El sistema SHALL permitir reasignar una tarea a otro docente, registrando la delegación (F8.2, HU-35).

#### Scenario: PROFESOR delega a colega
- **WHEN** el asignado actual envía `PUT /api/tareas/{id}/delegar` con nuevo_asignado_id
- **THEN** el sistema cambia asignado_a y agrega comentario automático de delegación

### Requirement: Admin global de tareas
El sistema SHALL permitir a COORDINADOR/ADMIN ver y filtrar todas las tareas del tenant (F8.3, HU-36).

#### Scenario: COORDINADOR lista todas las tareas
- **WHEN** un COORDINADOR envía `GET /api/tareas/admin`
- **THEN** devuelve todas las tareas del tenant con filtros opcionales

#### Scenario: Filtrar por docente asignado
- **WHEN** `GET /api/tareas/admin?asignado_a={user_id}`
- **THEN** solo devuelve tareas de ese docente

#### Scenario: Búsqueda libre
- **WHEN** `GET /api/tareas/admin?q=parcial`
- **THEN** busca en descripcion de tareas

### Requirement: Aislamiento multi-tenant
El sistema SHALL aislar tareas por tenant.

#### Scenario: Tenant A no ve tareas de tenant B
- **WHEN** usuario de tenant A consulta tareas
- **THEN** solo ve tareas de tenant A
