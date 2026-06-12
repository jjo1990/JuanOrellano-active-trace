## 1. Modelos Calificacion y UmbralMateria

- [x] 1.1 Crear `models/calificacion.py` con `Calificacion(BaseModelMixin, Base)`:
  - `__tablename__` = `"calificacion"`
  - `tenant_id`: UUID FK → tenant.id, NOT NULL
  - `entrada_padron_id`: UUID FK → entrada_padron.id, NOT NULL
  - `materia_id`: UUID FK → materia.id, NOT NULL
  - `actividad`: String(200), NOT NULL
  - `nota_numerica`: Numeric(5,2), NULLABLE
  - `nota_textual`: String(200), NULLABLE
  - `origen`: String(20), NOT NULL
  - `importado_at`: TIMESTAMP(timezone=True), server_default=func.now(), NOT NULL
  - `__table_args__`: CheckConstraint sobre `origen IN ('Importado', 'Manual')` + index sobre `(entrada_padron_id, materia_id)`

- [x] 1.2 Crear `models/umbral_materia.py` con `UmbralMateria(BaseModelMixin, Base)`:
  - `__tablename__` = `"umbral_materia"`
  - `tenant_id`: UUID FK → tenant.id, NOT NULL
  - `asignacion_id`: UUID FK → asignacion.id, NOT NULL
  - `materia_id`: UUID FK → materia.id, NOT NULL
  - `umbral_pct`: Integer, NOT NULL, server_default=60
  - `valores_aprobatorios`: JSONB, NOT NULL, server_default=sa.text("'[\"Satisfactorio\", \"Supera lo esperado\"]'::jsonb")
  - `__table_args__`: UniqueConstraint sobre `(asignacion_id, materia_id, tenant_id)` con nombre `uq_umbral_asignacion_materia`

- [x] 1.3 Actualizar `models/__init__.py` para exportar `Calificacion` y `UmbralMateria`

## 2. CalificacionesRepository

- [x] 2.1 (RED) Escribir `tests/test_calificaciones_modelos.py`:
  - Test crear Calificacion con nota_numerica
  - Test crear Calificacion con nota_textual
  - Test crear Calificacion con origen Importado/Manual
  - Test origen inválido viola CheckConstraint
  - Test soft delete Calificacion
  - Test crear UmbralMateria con valores default
  - Test crear UmbralMateria con valores custom
  - Test UniqueConstraint en umbral (misma asignacion+materia+tenant viola)
  - Test soft delete UmbralMateria

- [x] 2.2 (GREEN) Implementar `repositories/calificaciones_repository.py` con `CalificacionesRepository`:
  - `__init__(self, session, tenant_id)` — inicializa repos genéricos para Calificacion y UmbralMateria
  - `create_calificacion(entity: Calificacion) -> Calificacion`
  - `create_calificaciones_batch(entradas: list[Calificacion]) -> list[Calificacion]`
  - `get_umbral(asignacion_id, materia_id) -> UmbralMateria | None`
  - `upsert_umbral(entity: UmbralMateria) -> UmbralMateria`: crea o actualiza según UniqueConstraint
  - `get_calificaciones_by_entrada(entrada_padron_id) -> Sequence[Calificacion]`
  - `get_calificaciones_by_materia(materia_id) -> Sequence[Calificacion]`
  - `count_calificaciones(materia_id) -> int`

- [x] 2.3 (TRIANGULATE) Agregar tests: batch de 500+ calificaciones, soft delete umbral, query por materia con deleted_at=None

## 3. Esquemas Pydantic

- [x] 3.1 Crear `schemas/calificaciones.py` con:
  - `CalificacionDTO`: id, entrada_padron_id, materia_id, actividad, nota_numerica (opcional), nota_textual (opcional), aprobado (bool, computed), origen, importado_at — `model_config = ConfigDict(extra='forbid')`
  - `UmbralMateriaDTO`: id, asignacion_id, materia_id, umbral_pct, valores_aprobatorios — `extra='forbid'`
  - `UmbralMateriaUpdate`: umbral_pct (int, ge=0, le=100), valores_aprobatorios (list[str]) — `extra='forbid'`
  - `ColumnaDetectada`: name (str), tipo (Literal["numerica", "textual"]), aprobatorio (bool), actividad (str)
  - `ImportCalificacionesPreviewResponse`: preview_token, filename, detected_rows, columnas (list[ColumnaDetectada]), actividades (list[dict]), preview_rows (list[dict])
  - `ConfirmCalificacionesRequest`: actividades_seleccionadas (list[str])
  - `ConfirmCalificacionesResponse`: calificaciones_count, ignorados_count, materia_id, cohorte_id, importado_at
  - `ImportFinalizacionResponse`: calificaciones_count, ignorados_count, materia_id

## 4. CalificacionesService — Import pipeline

- [x] 4.1 (RED) Escribir `tests/test_calificaciones_import.py`:
  - Test upload xlsx con columnas (Real) detecta como numéricas (RN-01)
  - Test upload csv con columna Satisfactorio detecta como textual aprobatorio (RN-02)
  - Test preview retorna token con columnas detectadas y actividades
  - Test confirm con token válido persiste Calificaciones
  - Test confirm ignora filas sin EntradaPadron matching
  - Test confirm con token inválido retorna 404
  - Test confirm registra audit log CALIFICACIONES_IMPORTAR
  - Test upload sin permiso retorna 403
  - Test upload formato no soportado retorna 422

- [x] 4.2 (GREEN) Implementar parser de archivos en `services/calificaciones_service.py`:
  - `_parse_xlsx(file) -> list[dict]`: reutiliza patrón de C-09 (openpyxl read_only)
  - `_parse_csv(file) -> list[dict]`: reutiliza patrón de C-09 (csv.DictReader)
  - `_detect_format(filename) -> str`: por extensión (.xlsx, .csv)
  - `_detect_column_types(headers) -> list[ColumnaDetectada]`: aplica RN-01 (termina en "(Real)" → numérica) y RN-02 ("Satisfactorio"|"Supera lo esperado" → textual aprobatorio)
  - `_match_entradas(rows, materia_id, cohorte_id) -> dict`: match por nombre+apellidos contra EntradaPadron activa, retorna {matched, ignored}
  - Preview cache: `dict[str, dict]` en memoria con TTL 30 min

- [x] 4.3 (GREEN) Implementar CalificacionesService:
  - `async import_preview(file, materia_id, cohorte_id, asignacion_id, usuario_id) -> ImportCalificacionesPreviewResponse`
  - `async confirm_import(preview_token, actividades_seleccionadas) -> ConfirmCalificacionesResponse`: itera rows, crea Calificacion por cada entrada match, audit log
  - `async import_finalizacion(file, materia_id, cohorte_id, asignacion_id, usuario_id) -> ImportFinalizacionResponse`: detecta estado de finalización, crea Calificacion con nota_textual
  - `_es_aprobado(calificacion, umbral) -> bool`: lógica de derivación (D1 en design.md)
  - `async get_umbral(asignacion_id, materia_id) -> UmbralMateriaDTO`: retorna configurado o defaults
  - `async upsert_umbral(asignacion_id, materia_id, data: UmbralMateriaUpdate) -> UmbralMateriaDTO`

- [x] 4.4 (TRIANGULATE) Agregar tests: archivo vacío, encoding no UTF-8, filas con datos incompletos, batch de 500+ calificaciones, aprobado derivado correctamente

## 5. Calificaciones Router

- [x] 5.1 (RED) Escribir tests de integración para endpoints (httpx AsyncClient):
  - Test `POST /api/calificaciones/import` con archivo .xlsx retorna 200
  - Test `POST /api/calificaciones/import` sin permiso retorna 403
  - Test `POST /api/calificaciones/confirm/<token>` retorna 200 y persiste datos
  - Test `POST /api/calificaciones/import-finalizacion` retorna 200
  - Test `GET /api/calificaciones/umbral/<materia_id>` retorna 200 con defaults
  - Test `PUT /api/calificaciones/umbral/<materia_id>` crea/actualiza umbral
  - Test `PUT /api/calificaciones/umbral/<materia_id>` sin permiso retorna 403

- [x] 5.2 (GREEN) Implementar `api/v1/routers/calificaciones.py`:
  - `require_permission("calificaciones:importar")` en todos los endpoints
  - `POST /api/calificaciones/import`: multipart file + materia_id + cohorte_id + asignacion_id, delega a CalificacionesService.import_preview
  - `POST /api/calificaciones/confirm/<preview_token>`: body con actividades_seleccionadas, delega a CalificacionesService.confirm_import
  - `POST /api/calificaciones/import-finalizacion`: multipart file + materia_id + cohorte_id + asignacion_id, delega a CalificacionesService.import_finalizacion
  - `GET /api/calificaciones/umbral/<materia_id>`: query param asignacion_id, delega a service
  - `PUT /api/calificaciones/umbral/<materia_id>`: query param asignacion_id + body, delega a service
  - Inyectar dependencies: session, tenant_id, current_user

- [x] 5.3 Registrar router en `app/main.py` (o app factory)

## 6. Migration 010

- [x] 6.1 Crear `alembic/versions/010_create_calificacion_umbral.py`:
  - Revises: `009`
  - `upgrade()`: CREATE TABLE calificacion (id UUID PK, tenant_id UUID FK, entrada_padron_id UUID FK, materia_id UUID FK, actividad VARCHAR(200), nota_numerica NUMERIC(5,2), nota_textual VARCHAR(200), origen VARCHAR(20) NOT NULL, importado_at TIMESTAMPTZ, created_at, updated_at, deleted_at)
  - CheckConstraint `ck_calificacion_origen` ON calificacion: `origen IN ('Importado', 'Manual')`
  - CREATE TABLE umbral_materia (id UUID PK, tenant_id UUID FK, asignacion_id UUID FK, materia_id UUID FK, umbral_pct INTEGER NOT NULL DEFAULT 60, valores_aprobatorios JSONB NOT NULL DEFAULT '["Satisfactorio","Supera lo esperado"]'::jsonb, created_at, updated_at, deleted_at)
  - CREATE UNIQUE INDEX `uq_umbral_asignacion_materia` ON umbral_materia (asignacion_id, materia_id, tenant_id)
  - CREATE INDEX `ix_calificacion_entrada_materia` ON calificacion (entrada_padron_id, materia_id)
  - `downgrade()`: DROP TABLE calificacion, DROP TABLE umbral_materia

- [x] 6.2 Verificar `alembic upgrade head` ejecuta sin error
- [x] 6.3 Verificar `alembic downgrade -1` revierte correctamente

## 7. Tests de tenant isolation

- [x] 7.1 (RED) Escribir `tests/test_calificaciones_tenant.py`:
  - Test crear Calificacion en tenant A, repository de tenant B no la ve
  - Test crear UmbralMateria en tenant A, tenant B obtiene defaults
  - Test upsert umbral en tenant A no afecta tenant B
  - Test import en tenant A no afecta datos de tenant B

- [x] 7.2 (TRIANGULATE) Agregar escenarios borde: soft delete + create, list con filtros combinados, batch cross-tenant

## 8. Configuración y registro de permisos

- [x] 8.1 Verificar que `calificaciones:importar` está registrado en seed de permisos (RBAC seed existente)
- [x] 8.2 Verificar que `CALIFICACIONES_IMPORTAR` en `core/action_codes.py` se usa en los audit logs (ya existe)

## 9. Verificación final

- [x] 9.1 Ejecutar suite completa de tests (`pytest`) y confirmar verde (sin romper tests existentes)
- [x] 9.2 Verificar `alembic upgrade head` y `alembic downgrade -1`
- [x] 9.3 Confirmar que ningún archivo `.py` supera 500 LOC
- [x] 9.4 Confirmar que todos los Pydantic schemas nuevos usan `extra='forbid'`
- [x] 9.5 Confirmar que no hay hard delete en ningún repository
- [x] 9.6 Confirmar que `aprobado` NO se almacena en BD (es derivado en service layer)
- [x] 9.7 Confirmar que CheckConstraint en `calificacion.origen` está implementado
