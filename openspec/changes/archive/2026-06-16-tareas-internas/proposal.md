## Why

El sistema ya tiene asignaciones de docentes (C-07), equipos (C-08) y comunicaciones (C-12), pero no existe un mecanismo de coordinación interna mediante tareas: asignar trabajo a docentes, hacer seguimiento de estado, delegar entre colegas y mantener un hilo de comentarios. Sin los modelos `Tarea` y `ComentarioTarea`, la coordinación opera por canales externos (email, WhatsApp) sin trazabilidad ni auditoría. Este change modela el workflow completo de tareas internas (Épica 8), un módulo de alto uso con cientos de tareas simultáneas.

## What Changes

- **F8.1 — Mis tareas**: endpoint `GET /api/tareas/mis-tareas` para que el usuario vea las tareas que le fueron asignadas, filtrables por materia y estado. Acceso: cualquier usuario autenticado (self-data).
- **F8.2 — Delegar tarea**: endpoint `PUT /api/tareas/{id}/delegar` para reasignar una tarea a otro docente, dejando trazabilidad (el `asignado_por` original no cambia, pero se registra en comentarios). Acceso: el asignado actual o COORDINADOR.
- **F8.3 — Administración global**: endpoint `GET /api/tareas/admin` con filtros por docente asignado, asignador, materia, estado y búsqueda libre. `PUT /api/tareas/{id}/estado` para cambiar estado. Guard: `tareas:gestionar` (COORDINADOR, ADMIN).
- **CRUD de tareas**: `POST /api/tareas` (crear), `GET /api/tareas/{id}` (detalle con comentarios), `PUT /api/tareas/{id}` (editar).
- **Comentarios**: `POST /api/tareas/{id}/comentarios` para agregar comentarios al hilo de la tarea. `GET /api/tareas/{id}/comentarios` para listar.
- **Nuevos modelos**: `Tarea` (materia_id, asignado_a, asignado_por, estado, descripcion, contexto_id) y `ComentarioTarea` (tarea_id, autor_id, texto).
- **Nuevo permiso**: `tareas:gestionar` (COORDINADOR, ADMIN).
- **Nueva migración Alembic**: tablas `tarea` y `comentario_tarea` + seed de permiso.

## Capabilities

### New Capabilities

- `tareas-crud`: ABM de tareas con asignación, delegación y cambio de estado. Filtros avanzados para admin global.
- `tareas-comentarios`: hilo de comentarios por tarea con trazabilidad de autor y timestamp.

### Modified Capabilities

Ninguna.

## Impact

- **Nuevo código**: `models/tarea.py`, `models/comentario_tarea.py`, `schemas/tarea.py`, `api/v1/routers/tareas.py`, `services/tarea_service.py`, `repositories/tarea_repository.py`, `repositories/comentario_tarea_repository.py`.
- **Modificado**: `models/__init__.py`, `core/action_codes.py`, `main.py`.
- **Migración**: tablas `tarea` y `comentario_tarea` + seed `tareas:gestionar`.
- **Dependencia**: C-07 (`User`, `Materia`). Sin cambios en modelos existentes.
- **Governance**: MEDIO — lógica de dominio con state machine simple, sin datos sensibles.
