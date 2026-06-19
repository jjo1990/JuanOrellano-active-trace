## Why

C-07 construyó la gestión individual de asignaciones (CRUD sobre el modelo `Asignacion`). Pero el coordinador no administra docentes de a uno: necesita operar a nivel de equipo — ver sus propios equipos, asignar docentes en bloque, clonar entre períodos académicos, modificar vigencias masivamente y exportar. Sin estas capacidades, el flujo de setup de cuatrimestre (FL-03) requiere intervención manual repetitiva para cada docente, lo que anula el valor de tener las asignaciones modeladas.

## What Changes

- **F4.2 — Mis equipos**: endpoint `GET /api/equipos/mis-equipos` que devuelve la vista enriquecida de las asignaciones del usuario autenticado, con joins a `user`, `rol`, `materia`, `carrera` y `cohorte` para mostrar nombres en vez de UUIDs. Accesible para cualquier usuario autenticado (PROFESOR, TUTOR, NEXO, COORDINADOR) — es _self-data_, no requiere permiso especial.
- **F4.4 — Asignación masiva**: endpoint `POST /api/equipos/asignacion-masiva` que recibe una lista de `usuario_id` + un contexto común (`materia_id`, `carrera_id`, `cohorte_id`, `rol_id`, `desde`, `hasta`, `comisiones`) y crea todas las asignaciones en una transacción. Con autocompletado de búsqueda de usuarios (RN-30). Guard: `equipos:asignar` (COORDINADOR, ADMIN).
- **F4.5 — Clonar equipo**: endpoint `POST /api/equipos/clonar` que duplica todas las asignaciones de un equipo origen (`materia_id × carrera_id × cohorte_id`) hacia un destino (misma materia/carrera, diferente cohorte), respetando RN-12. Guard: `equipos:asignar`.
- **F4.6 — Modificar vigencia general**: endpoint `PUT /api/equipos/vigencia` que actualiza `desde`/`hasta` para todas las asignaciones que coinciden con los filtros de equipo (`materia_id`, `carrera_id`, `cohorte_id`) en una sola operación. Guard: `equipos:asignar`.
- **F4.7 — Exportar equipo**: endpoint `GET /api/equipos/exportar` que genera un archivo descargable (CSV) con el detalle del equipo: docente, rol, materia, carrera, cohorte, comisiones, vigencia y estado derivado. Guard: `equipos:asignar`.
- **Autocompletado de usuarios** (RN-30): endpoint auxiliar `GET /api/equipos/buscar-usuarios?q=` para que el frontend de asignación masiva busque usuarios por nombre/apellido.
- **Nuevo permiso `equipos:ver_propio`**: otorgado a PROFESOR, TUTOR, NEXO, COORDINADOR para F4.2. Distinto de `equipos:asignar` para separar la vista propia de la administración.
- **Nueva migración Alembic**: agrega el permiso `equipos:ver_propio` y sus asignaciones RolPermiso correspondientes.

## Capabilities

### New Capabilities

- `mis-equipos`: vista enriquecida de las asignaciones del usuario autenticado con joins a entidades relacionadas. Filtros: estado, materia, rol, carrera, cohorte.
- `asignacion-masiva`: creación en bloque de asignaciones para múltiples usuarios contra un mismo contexto académico, con validación FK por cada usuario y reporte de errores por docente.
- `clonar-equipo`: duplicación de todas las asignaciones de un equipo origen hacia un destino con diferente cohorte, aplicando RN-12. Clona solo asignaciones no eliminadas.
- `modificar-vigencia-equipo`: actualización masiva de fechas `desde`/`hasta` para todas las asignaciones de un equipo seleccionado por materia × carrera × cohorte.
- `exportar-equipo`: generación de archivo CSV descargable con el detalle completo del equipo docente. Columnas: nombre, apellido, email, rol, materia, carrera, cohorte, comisiones, desde, hasta, estado.
- `busqueda-usuarios`: endpoint de autocompletado server-side para buscar usuarios por nombre, apellido o legajo, requerido por la UI de asignación masiva (RN-30).

### Modified Capabilities

- `asignaciones` (C-07): el repositorio `AsignacionRepository` se extiende con métodos `list_with_joins`, `bulk_create`, `bulk_update_vigencia`, `list_by_equipo`. El modelo y los endpoints existentes no cambian.

## Impact

- **Nuevo código**: `schemas/equipo.py`, `api/v1/routers/equipos.py`, `services/equipo_service.py`.
- **Modificado**: `repositories/asignacion_repository.py` (nuevos métodos), `repositories/user_repository.py` (método de búsqueda por nombre), `models/__init__.py` (exports).
- **Nuevo permiso**: `equipos:ver_propio` (migración Alembic para insertar el permiso + RolPermiso).
- **Migración**: nueva migración que inserta `equipos:ver_propio` en las tablas `permiso` y `rol_permiso`.
- **Dependencia**: C-07 (`Asignacion`, `AsignacionRepository`, `AsignacionService`). Sin cambios en modelos existentes.
- **Habilita**: C-23 `frontend-coordinacion` (necesita estos endpoints para la UI de gestión de equipos).
- **Governance**: ALTO — requiere revisión antes de escribir código (operaciones masivas sobre asignaciones, permisos).
