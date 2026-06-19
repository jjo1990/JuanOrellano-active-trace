## ADDED Requirements

### Requirement: Vista mis-tareas y administración global
El sistema SHALL mostrar las tareas asignadas al usuario y permitir al COORDINADOR ver todas las tareas del tenant con filtros.

#### Scenario: Mis tareas pendientes
- **WHEN** el usuario accede a "Mis Tareas"
- **THEN** el sistema muestra tabla con columnas: Título, Asignado por, Estado, Fecha, Acciones.

#### Scenario: Administración global con filtros
- **WHEN** el COORDINADOR filtra por estado "En progreso" y materia
- **THEN** el sistema muestra solo las tareas que coinciden, de todos los docentes.

### Requirement: Workflow de estados
El sistema SHALL permitir cambiar el estado de una tarea (Pendiente → En progreso → Resuelta, o → Cancelada).

#### Scenario: Avanzar estado
- **WHEN** el usuario cambia una tarea de "Pendiente" a "En progreso"
- **THEN** el sistema actualiza el estado y opcionalmente agrega un comentario.

### Requirement: Delegar tarea
El sistema SHALL permitir reasignar una tarea a otro docente.

#### Scenario: Delegar tarea
- **WHEN** el usuario selecciona "Delegar", busca un docente y confirma
- **THEN** el sistema actualiza `asignado_a` y registra un comentario automático de delegación.
