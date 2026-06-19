## Why

C-07 construyó las asignaciones de docentes a materias y C-13 los encuentros sincrónicos, pero el sistema aún no modela las instancias formales de evaluación oral: coloquios, parciales y recuperatorios. Sin los modelos `Evaluacion`, `ReservaEvaluacion` y `ResultadoEvaluacion`, el coordinador no puede convocar alumnos a rendir, los alumnos no pueden reservar turno, y no hay registro consolidado de notas finales de coloquio. Este change cierra la Épica 7 modelando el ciclo completo: convocatoria → reserva de turno → registro de resultado.

## What Changes

- **F7.3 — Crear convocatoria de coloquio**: endpoint `POST /api/coloquios/evaluaciones` para que COORDINADOR/ADMIN definan una instancia de evaluación con materia, cohorte, tipo, instancia, días disponibles y cupos por día. Guard: `coloquios:gestionar`.
- **F7.2 — Importar alumnos a convocatoria**: endpoint `POST /api/coloquios/evaluaciones/{id}/alumnos` para cargar el padrón de alumnos habilitados para una convocatoria. Guard: `coloquios:gestionar`.
- **Reserva de turno por ALUMNO** (HU-47): endpoint `POST /api/coloquios/reservas` para que un ALUMNO reserve un turno en un día con cupo disponible. Endpoint `DELETE /api/coloquios/reservas/{id}` para cancelar reserva. Guard: `coloquios:reservar` (ALUMNO). Responde PA-14: la reserva se hace dentro del sistema.
- **F7.4 — Listado de convocatorias**: endpoint `GET /api/coloquios/evaluaciones` con vista tabular que incluye métricas: materia, instancia, días disponibles, convocados, reservas activas, cupos libres.
- **F7.5 — Administración global**: endpoints `PUT /api/coloquios/evaluaciones/{id}` (editar/cerrar convocatoria), `GET /api/coloquios/agenda` (agenda consolidada de reservas con filtros), `GET /api/coloquios/resultados` (registro académico consolidado con notas finales).
- **Registro de resultado**: endpoint `POST /api/coloquios/resultados` para que COORDINADOR/ADMIN registren la nota final de un alumno en una evaluación.
- **F7.1 — Panel de métricas**: endpoint `GET /api/coloquios/metricas` con totales: alumnos cargados, instancias activas, reservas activas, notas registradas.
- **Nuevos modelos SQLAlchemy**: `Evaluacion`, `ReservaEvaluacion`, `ResultadoEvaluacion` con `BaseModelMixin`.
- **Nuevos permisos**: `coloquios:gestionar` (COORDINADOR, ADMIN) y `coloquios:reservar` (ALUMNO).
- **Nueva migración Alembic**: tablas `evaluacion`, `reserva_evaluacion`, `resultado_evaluacion` + seed de permisos.

## Capabilities

### New Capabilities

- `convocatorias-coloquio`: CRUD de evaluaciones con tipo (Parcial/TP/Coloquio/Recuperatorio), días disponibles, cupos por día. Importación de alumnos habilitados. Métricas por convocatoria (F7.2, F7.3, F7.4).
- `reservas-coloquio`: reserva de turno por ALUMNO con validación de cupo (resta del cupo disponible). Cancelación de reserva. Estado Activa/Cancelada (HU-47, F7.5 agenda).
- `resultados-coloquio`: registro de nota final por alumno en una evaluación. Consulta de registro académico consolidado (F7.5 resultados).
- `metricas-coloquio`: panel con totales agregados: alumnos cargados, instancias activas, reservas activas, notas registradas (F7.1).

### Modified Capabilities

Ninguna — este change introduce capacidades nuevas sin modificar specs existentes.

## Impact

- **Nuevo código**: `models/evaluacion.py`, `models/reserva_evaluacion.py`, `models/resultado_evaluacion.py`, `schemas/coloquio.py`, `api/v1/routers/coloquios.py`, `services/coloquio_service.py`, `repositories/evaluacion_repository.py`, `repositories/reserva_evaluacion_repository.py`, `repositories/resultado_evaluacion_repository.py`.
- **Modificado**: `models/__init__.py` (exports), `core/action_codes.py` (nuevos permisos), `main.py` (router).
- **Nuevos permisos**: `coloquios:gestionar` (COORDINADOR, ADMIN) y `coloquios:reservar` (ALUMNO) vía migración de datos.
- **Migración**: nueva migración Alembic que crea las tablas `evaluacion`, `reserva_evaluacion`, `resultado_evaluacion` con FK a `materia`, `cohorte` y `user`.
- **Dependencia**: C-07 (`Asignacion`, `User`, `Materia`, `Cohorte`). Sin cambios en modelos existentes.
- **Habilita**: C-23 `frontend-coordinacion` (necesita endpoints de coloquios para la UI de coordinación).
- **Governance**: MEDIO — lógica de dominio con reglas de negocio (cupo, reserva, resultados), sin datos PII ni operaciones financieras.
