## 1. Modelos SQLAlchemy

- [x] 1.1 Crear `models/tarea.py` con modelo `Tarea(BaseModelMixin)`:
  - `__tablename__` = "tarea"
  - `materia_id`: UUID FK → materia.id, nullable
  - `asignado_a`: UUID FK → user.id, NOT NULL
  - `asignado_por`: UUID FK → user.id, NOT NULL
  - `estado`: str (enum: Pendiente/En progreso/Resuelta/Cancelada), default="Pendiente"
  - `descripcion`: str, NOT NULL
  - `contexto_id`: UUID, nullable
  - `__table_args__`: Index en tenant_id+asignado_a+estado, Index en tenant_id+materia_id, Index en tenant_id+estado

- [x] 1.2 Crear `models/comentario_tarea.py` con modelo `ComentarioTarea(BaseModelMixin)`:
  - `__tablename__` = "comentario_tarea"
  - `tarea_id`: UUID FK → tarea.id, NOT NULL
  - `autor_id`: UUID FK → user.id, NOT NULL
  - `texto`: str, NOT NULL
  - `__table_args__`: Index en tenant_id+tarea_id

- [x] 1.3 Actualizar `models/__init__.py` para exportar Tarea, ComentarioTarea

## 2. Migración Alembic

- [x] 2.1 Generar migración: CREATE TABLE tarea, comentario_tarea con FK e índices
- [x] 2.2 Insertar permiso `tareas:gestionar` + RolPermiso (COORDINADOR, ADMIN). Idempotente.
- [ ] 2.3 Verificar `alembic upgrade head` (DB en estado inconsistente — requiere rebuild; los tests usan `Base.metadata.create_all`)
- [ ] 2.4 Verificar `alembic downgrade -1` (idem)

## 3. Action Codes

- [x] 3.1 Agregar `TAREAS_GESTIONAR = "tareas:gestionar"` en `core/action_codes.py`

## 4. Repositories

- [x] 4.1 (RED) `tests/test_tarea_repository.py`: crear, listar por asignado_a, filtrar por estado, soft delete
- [x] 4.2 (GREEN) `repositories/tarea_repository.py`: `list_by_asignado`, `list_with_filters`
- [x] 4.3 (RED) `tests/test_comentario_tarea_repository.py`: crear, listar por tarea_id ordenados
- [x] 4.4 (GREEN) `repositories/comentario_tarea_repository.py`

## 5. Schemas Pydantic

- [x] 5.1 Crear `schemas/tarea.py` con:
  - `TareaCreateRequest`: materia_id (opc), asignado_a, descripcion, contexto_id (opc). `extra='forbid'`
  - `TareaUpdateRequest`: descripcion (opc), materia_id (opc). `extra='forbid'`
  - `TareaDelegarRequest`: nuevo_asignado_id. `extra='forbid'`
  - `TareaEstadoRequest`: estado. `extra='forbid'`
  - `TareaResponse`: id + todos los campos + comentarios
  - `ComentarioCreateRequest`: texto. `extra='forbid'`
  - `ComentarioResponse`: id, tarea_id, autor_id, texto, creado_at

## 6. Service

- [x] 6.1 (RED) `tests/test_tarea_service.py`:
  - Crear tarea
  - Listar mis tareas con filtros
  - Cambiar estado (asignado)
  - Cambiar estado (no asignado sin permiso): espera 403
  - Cambiar estado (COORDINADOR): OK
  - Delegar tarea (asignado actual): OK, crea comentario auto
  - Delegar tarea (no asignado): espera 403
  - Admin listar con filtros combinados
  - Agregar comentario
  - Listar comentarios

- [x] 6.2 (GREEN) `services/tarea_service.py` ≤250 LOC (189 LOC)

## 7. Router

- [x] 7.1 `api/v1/routers/tareas.py`:
  - `POST /api/tareas` → TareaCreateRequest → TareaResponse
  - `GET /api/tareas/mis-tareas` → list[TareaResponse] (self, F8.1)
  - `GET /api/tareas/{id}` → TareaResponse con comentarios
  - `PUT /api/tareas/{id}` → TareaUpdateRequest → TareaResponse
  - `PUT /api/tareas/{id}/estado` → TareaEstadoRequest → TareaResponse
  - `PUT /api/tareas/{id}/delegar` → TareaDelegarRequest → TareaResponse (F8.2)
  - `GET /api/tareas/admin` → list[TareaResponse]. Guard: `tareas:gestionar` (F8.3)
  - `POST /api/tareas/{id}/comentarios` → ComentarioCreateRequest → ComentarioResponse
  - `GET /api/tareas/{id}/comentarios` → list[ComentarioResponse]

- [x] 7.2 Registrar router en `main.py`

## 8. Tests y verificación

- [x] 8.1 Tests repositorio (tarea + comentario) — 10/10
- [x] 8.2 Tests servicio (workflow, delegación, permisos) — 16/16
- [x] 8.3 `pytest` verde — 26/26 passed
- [x] 8.4 Cobertura ≥80%
- [x] 8.5 ≤500 LOC (max 189 LOC en service)
- [x] 8.6 Schemas `extra='forbid'` — 7/7
- [x] 8.7 Sin hard delete
- [x] 8.8 Identidad desde JWT (get_current_user / require_permission)
