## Context

C-07 construyó usuarios y asignaciones. C-16 modela el workflow de tareas internas entre coordinación y docentes. Es un módulo de alto uso: cientos de tareas simultáneas durante el período activo.

**Restricciones**: modelos nuevos con BaseModelMixin. Router bajo `/api/tareas`. Sin dependencias nuevas.

## Goals / Non-Goals

**Goals:**
- Modelos `Tarea` y `ComentarioTarea`.
- `POST /api/tareas` — crear tarea (cualquier usuario autenticado).
- `GET /api/tareas/mis-tareas` — tareas asignadas al usuario (F8.1). Filtros: materia_id, estado.
- `GET /api/tareas/{id}` — detalle con comentarios.
- `PUT /api/tareas/{id}` — editar campos (asignado_a, descripcion, materia_id).
- `PUT /api/tareas/{id}/estado` — cambiar estado (F8.3). Guard: `tareas:gestionar` o el asignado.
- `PUT /api/tareas/{id}/delegar` — reasignar a otro docente (F8.2).
- `GET /api/tareas/admin` — vista global con filtros (F8.3). Guard: `tareas:gestionar`.
- `POST /api/tareas/{id}/comentarios` — agregar comentario.
- `GET /api/tareas/{id}/comentarios` — listar comentarios.
- Nuevo permiso `tareas:gestionar` (COORDINADOR, ADMIN).

**Non-Goals:**
- Sin notificaciones al asignado (→ C-12).
- Sin UI (→ C-23).
- Sin adjuntos en comentarios.
- Sin fechas de vencimiento (futuro).

## Decisions

### D1 — Estados: Pendiente → En progreso → Resuelta (o Cancelada)

Ciclo de vida: `Pendiente` (initial) → `En progreso` → `Resuelta`. Desde cualquier estado se puede pasar a `Cancelada`. Se resuelve PA-08 con este modelo simple.

### D2 — Delegar: cambia asignado_a, registra en comentario

`PUT /api/tareas/{id}/delegar` recibe `nuevo_asignado_id`. Cambia `asignado_a` y agrega automáticamente un comentario del sistema: "Tarea delegada de X a Y por Z".

### D3 — Comentarios: endpoint separado

`POST /api/tareas/{id}/comentarios` crea un `ComentarioTarea`. No se mezcla con el PUT de la tarea. Esto mantiene la separación de concerns y permite agregar comentarios sin cambiar otros campos.

### D4 — Admin global: filtros compuestos

`GET /api/tareas/admin` acepta query params: `asignado_a`, `asignado_por`, `materia_id`, `estado`, `q` (búsqueda en descripción). Todos opcionales. Se combinan con AND.

### D5 — Layout

```
backend/app/
├── api/v1/routers/tareas.py
├── services/tarea_service.py
├── schemas/tarea.py
├── repositories/{tarea_repository,comentario_tarea_repository}.py
├── models/{tarea,comentario_tarea}.py
└── tests/{test_tarea_repository,test_tarea_service}.py
```

### D6 — Permiso: `tareas:gestionar`

Constante `TAREAS_GESTIONAR = "tareas:gestionar"`. COORDINADOR y ADMIN. Los endpoints self-service (mis-tareas, crear, comentar) no requieren permiso especial.

## Risks / Trade-offs

- **[Alto volumen de tareas]**: cientos simultáneas — Mitigación: índices en tenant_id+estado, tenant_id+asignado_a, tenant_id+materia_id. Paginación en admin.
- **[Delegación sin validación de jerarquía]**: cualquier asignado puede delegar a cualquier usuario — Mitigación: para MVP es aceptable. Se puede agregar restricción de roles en el futuro.

## Migration Plan

1. Migración schema: tablas `tarea` y `comentario_tarea`.
2. Seed `tareas:gestionar` + RolPermiso. Idempotente.
3. Deploy aditivo. Rollback: downgrade + quitar router.
