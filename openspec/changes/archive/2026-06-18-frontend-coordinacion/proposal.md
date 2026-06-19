## Why

COORDINADORES y ADMIN necesitan gestionar el ecosistema completo de la coordinación académica desde el frontend: armar equipos docentes, publicar avisos, gestionar tareas internas, monitorear el progreso de todas las materias, administrar encuentros y coloquios, y configurar el setup del cuatrimestre. El backend ya expone todos estos endpoints (C-08, C-13, C-14, C-15, C-16, C-17). C-23 es el segundo feature module productivo, complementario a C-22 (vista del profesor).

## What Changes

- **Nuevo feature module** `features/coordinacion/` con estructura feature-based
- **Gestión de equipos docentes**: mis-equipos, asignación masiva, clonar entre períodos, modificar vigencia, exportar (F4.2-F4.7)
- **Gestión de avisos**: ABM con scope (Global/PorMateria/PorCohorte/PorRol), severidad, vigencia y acknowledgment (F3.5)
- **Gestión de tareas internas**: mis tareas, asignar/delegar, workflow de estados, comentarios (F8.1-F8.3)
- **Monitores transversales**: vista general de todas las materias y seguimiento por docente (F2.7, F2.9)
- **Gestión de encuentros**: crear recurrente/único, editar instancias, vista admin, registro de guardias (F6.1-F6.6)
- **Gestión de coloquios**: crear convocatorias, importar alumnos, reserva de turnos, métricas (F7.1-F7.5)
- **Programas y fechas académicas**: upload de programas, ABM de fechas académicas (F5.3, F5.4)
- **Setup de cuatrimestre**: flujo guiado para configurar un nuevo período (FL-03)
- **Rutas**: integración en el router con guards de permiso de COORDINADOR/ADMIN

## Capabilities

### New Capabilities
- `gestion-equipos`: UI para gestión de equipos docentes: vista mis-equipos, asignación masiva, clonar períodos, modificar vigencia y exportar.
- `gestion-avisos`: ABM de avisos con configuración de scope, severidad, vigencia, require_ack y vista de acknowledgments.
- `gestion-tareas`: Vista mis-tareas, asignar/delegar, workflow de estados (Pendiente→En progreso→Resuelta/Cancelada) y comentarios en hilo.
- `monitores-transversales`: Vistas de monitoreo general de todas las materias y seguimiento por docente con filtros avanzados.
- `gestion-encuentros`: Crear encuentros recurrentes/únicos, editar instancias, vista admin de calendario y registro de guardias con export.
- `gestion-coloquios`: Crear convocatorias con cupos, importar alumnos, panel de reservas y métricas de coloquios.
- `gestion-programas`: Upload y asociación de programas de materia, ABM de fechas académicas (parciales, TP, coloquios).
- `setup-cuatrimestre`: Flujo guiado paso a paso para configurar cohorte, asignar docentes, importar padrón y definir fechas.

### Modified Capabilities
<!-- None -->

## Impact

- **Nuevo directorio**: `frontend/src/features/coordinacion/` (components, hooks, pages, services, types)
- **Rutas nuevas**: `/equipos`, `/avisos`, `/tareas`, `/monitores`, `/encuentros`, `/coloquios`, `/programas`, `/setup`
- **Dependencias backend**: C-08, C-11 (monitores), C-13, C-14, C-15, C-16, C-17
- **Dependencias frontend**: C-21 (shell + auth), reusa DataTable, StatusBadge de C-22
- **Menú**: nueva sección "Coordinación" en sidebar con dropdown de módulos
