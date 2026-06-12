## 1. Modelos VersionPadron y EntradaPadron

- [x] 1.1 Crear `models/version_padron.py` con `VersionPadron(BaseModelMixin, Base)`:
  - `__tablename__` = `"version_padron"`
  - `tenant_id`: UUID FK → tenant.id, NOT NULL
  - `materia_id`: UUID FK → materia.id, NOT NULL
  - `cohorte_id`: UUID FK → cohorte.id, NOT NULL
  - `cargado_por`: UUID FK → user.id, NOT NULL
  - `cargado_at`: TIMESTAMP(timezone=True), server_default=func.now()
  - `activa`: Boolean, default=True, NOT NULL
  - `__table_args__`: UniqueConstraint parcial `uq_version_activa_materia_cohorte` sobre (materia_id, cohorte_id, tenant_id) WHERE activa = true

- [x] 1.2 Crear `models/entrada_padron.py` con `EntradaPadron(BaseModelMixin, Base)`:
  - `__tablename__` = `"entrada_padron"`
  - `tenant_id`: UUID FK → tenant.id, NOT NULL
  - `version_id`: UUID FK → version_padron.id, NOT NULL
  - `usuario_id`: UUID FK → user.id, NULLABLE
  - `nombre`: String(100), NOT NULL
  - `apellidos`: String(200), NOT NULL
  - `email_encrypted`: String(512), NULLABLE — columna companion para EncryptedField
  - `email`: EncryptedField() — descriptor que cifra/descifra automáticamente
  - `comision`: String(50), NULLABLE
  - `regional`: String(100), NULLABLE

- [x] 1.3 Actualizar `models/__init__.py` para exportar `VersionPadron` y `EntradaPadron`

## 2. PadronRepository

- [x] 2.1 (RED) Escribir `tests/test_padron_versionado.py`:
  - Test crear VersionPadron con activa=True
  - Test activar nueva versión desactiva la anterior (misma materia×cohorte×tenant)
  - Test activar versión en tenant A no afecta tenant B
  - Test crear EntradaPadron asociada a versión
  - Test EntradaPadron con usuario_id=None
  - Test EntradaPadron con usuario_id válido del mismo tenant

- [x] 2.2 (GREEN) Implementar `repositories/padron_repository.py` con `PadronRepository`:
  - `__init__(self, session, tenant_id)` — inicializa repos genéricos para VersionPadron y EntradaPadron
  - `get_active_version(materia_id, cohorte_id) -> VersionPadron | None`
  - `create_version(entity: VersionPadron) -> VersionPadron`: si ya hay activa, la desactiva (activa=False), luego crea la nueva
  - `get_version(id) -> VersionPadron | None`
  - `list_versions(materia_id=None) -> Sequence[VersionPadron]`
  - `create_entrada(entity: EntradaPadron) -> EntradaPadron`
  - `list_entradas(version_id) -> Sequence[EntradaPadron]`
  - `soft_delete_by_materia(materia_id) -> int`: soft delete de todas las versiones+entradas de una materia, retorna filas afectadas
  - `count_entradas(version_id) -> int`

- [x] 2.3 (TRIANGULATE) Agregar: list_versions con filtros, crear múltiples entradas en batch, soft_delete_by_materia con filas_afectadas correcto

## 3. Esquemas Pydantic y auditoría

- [x] 3.1 Crear `schemas/padron.py` con:
  - `VersionPadronDTO`: id, materia_id, cohorte_id, cargado_por, cargado_at, activa — `model_config = ConfigDict(extra='forbid')`
  - `EntradaPadronDTO`: id, version_id, usuario_id (opcional), nombre, apellidos, email, comision, regional
  - `ImportPreviewResponse`: preview_token, filename, detected_rows, columns, preview_rows: list[dict]
  - `ConfirmResponse`: version_id, entries_count, materia_id, cohorte_id, cargado_at
  - `VaciarResponse`: materia_id, filas_afectadas, mensaje

- [x] 3.2 Agregar `PADRON_CARGAR` a las constantes de action codes de auditoría (en schemas/audit.py o constantes)

## 4. PadronService — Import pipeline

- [x] 4.1 (RED) Escribir `tests/test_padron_import.py`:
  - Test upload xlsx válido retorna preview token
  - Test upload csv válido (delimitado por coma y por punto y coma)
  - Test upload con columnas faltantes retorna 422
  - Test confirm con token válido persiste versión + entradas
  - Test confirm con token inválido retorna 404
  - Test confirm desactiva versión anterior de la materia
  - Test import registra audit log PADRON_CARGAR

- [x] 4.2 (GREEN) Implementar parser de archivos en `services/padron_service.py`:
  - `_parse_xlsx(file: UploadFile) -> list[dict]`: usa openpyxl, lee filas, mapea columnas
  - `_parse_csv(file: UploadFile) -> list[dict]`: usa csv.Sniffer para detectar dialecto, mapea columnas
  - `_detect_format(filename) -> str`: por extensión (.xlsx, .csv)
  - `_validate_columns(headers, required) -> None`: raise si faltan columnas requeridas
  - Preview cache: `dict[str, dict]` en memoria con TTL 30 min (limpieza vía background task o thread)

- [x] 4.3 (GREEN) Implementar PadronService:
  - `async import_preview(file, materia_id, cohorte_id, usuario_id) -> ImportPreviewResponse`
  - `async confirm_import(preview_token) -> ConfirmResponse`: recupera preview, crea VersionPadron (con desactivación de anterior via repo), crea EntradaPadron batch, registra audit log, invalida token
  - `async vaciar_materia(materia_id, usuario_id) -> VaciarResponse`: verifica scope (profesor solo propia, coordinador cualquiera), soft delete via repo, audit log
  - `async get_entradas(version_id) -> Sequence[EntradaPadronDTO]`

- [x] 4.4 (TRIANGULATE) Agregar tests: archivo vacío, encoding no UTF-8, filas con datos incompletos (nombre faltante), batch de 500+ entradas

## 5. Moodle WS Integration

- [x] 5.1 Crear `integrations/__init__.py` (si no existe)
- [x] 5.2 (RED) Escribir `tests/test_moodle_ws.py`:
  - Test MoodleClient.get_enrolled_users retorna lista mapeada
  - Test Moodle WS timeout lanza MoodleWSException
  - Test Moodle WS HTTP error (401, 500) mapea a 502
  - Test retry con backoff: 3 intentos, falla después del último

- [x] 5.3 (GREEN) Implementar `integrations/moodle_ws.py`:
  - `class MoodleWSException(Exception)`: error específico de Moodle WS
  - `class MoodleClient`:
    - `__init__(self, base_url: str, token: str)`
    - `async get_enrolled_users(course_id: str | int) -> list[dict]`: llama `core_enrol_get_enrolled_users`, mapea response a formato interno
    - `async get_activities(course_id) -> list[dict]`: llama `core_course_get_contents` o similar
    - `async get_grades(course_id) -> list[dict]`: para C-10
    - Manejo de errores: timeout (30s), HTTP errors, connection refused → MoodleWSException
    - Retry: `tenacity` con 3 intentos, backoff (1, 5, 15s)

- [x] 5.4 Agregar `MOODLE_WS_TIMEOUT=30` y `MOODLE_WS_MAX_RETRIES=3` a configuración en `core/config.py`
- [x] 5.5 Agregar `tenacity` a `pyproject.toml`

## 6. Padron Router

- [x] 6.1 (RED) Escribir tests de integración para endpoints (usando httpx AsyncClient contra la app):
  - Test `POST /api/padron/import` con archivo .xlsx retorna 200
  - Test `POST /api/padron/import` sin permiso retorna 403
  - Test `POST /api/padron/confirm/<token>` retorna 200 y persiste datos
  - Test `DELETE /api/padron/vaciar/<materia_id>` retorna 200
  - Test `DELETE /api/padron/vaciar/<materia_id>` sin permiso retorna 403
  - Test `POST /api/padron/sync-moodle/<materia_id>` sin WS config retorna error

- [x] 6.2 (GREEN) Implementar `routers/padron.py`:
  - `require_permission("padron:importar")` en todos los endpoints
  - `POST /api/padron/import`: recibe multipart file + materia_id + cohorte_id, delega a PadronService.import_preview
  - `POST /api/padron/confirm/<preview_token>`: delega a PadronService.confirm_import
  - `DELETE /api/padron/vaciar/<materia_id>`: delega a PadronService.vaciar_materia
  - `POST /api/padron/sync-moodle/<materia_id>`: lee config moodle del tenant, instancia MoodleClient, ejecuta sync, persiste via PadronService
  - Inyectar dependencies: session, tenant_id, current_user

- [x] 6.3 Registrar router en `app/main.py`

## 7. Migration 009

- [x] 7.1 Crear `alembic/versions/009_create_version_padron_entrada.py`:
  - `upgrade()`: CREATE TABLE version_padron (id UUID PK, tenant_id UUID FK, materia_id UUID FK, cohorte_id UUID FK, cargado_por UUID FK, cargado_at TIMESTAMPTZ, activa BOOLEAN DEFAULT TRUE, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ, deleted_at TIMESTAMPTZ)
  - CREATE TABLE entrada_padron (id UUID PK, version_id UUID FK, tenant_id UUID FK, usuario_id UUID FK nullable, nombre VARCHAR(100), apellidos VARCHAR(200), email_encrypted VARCHAR(512), comision VARCHAR(50), regional VARCHAR(100), created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ, deleted_at TIMESTAMPTZ)
  - CREATE UNIQUE INDEX `uq_version_padron_activa` ON version_padron (materia_id, cohorte_id, tenant_id) WHERE activa = true
  - CREATE INDEX `ix_entrada_padron_version` ON entrada_padron (version_id)
  - CREATE INDEX `ix_entrada_padron_materia` ON entrada_padron (tenant_id) — se filtra por tenant siempre
  - `downgrade()`: DROP TABLE entrada_padron, DROP TABLE version_padron

- [x] 7.2 Verificar `alembic upgrade head` ejecuta sin error
- [x] 7.3 Verificar `alembic downgrade -1` revierte correctamente

## 8. Nightly sync worker

- [x] 8.1 Crear `workers/nightly_sync.py`:
  - Función `run_nightly_sync()` que itera sobre tenants con moodle configurado en `tenant.config["moodle"]`
  - Para cada materia con WS config, ejecuta `PadronService.sync_from_moodle(materia_id, cohorte_id)`
  - Registra resultados en audit log (éxitos y fallos)
  - Timeout total por tenant: 5 minutos

- [x] 8.2 Registrar worker en schedule (cron expression o background loop en docker)

## 9. Tests de tenant isolation y verificación final

- [x] 9.1 (RED) Escribir `tests/test_padron_tenant.py`:
  - Test crear VersionPadron en tenant A, repository de tenant B no la ve
  - Test crear EntradaPadron en tenant A, list en tenant B no la incluye
  - Test vaciar materia en tenant A no afecta tenant B
  - Test versión activa en tenant A no se desactiva al crear en tenant B

- [x] 9.2 (TRIANGULATE) Agregar escenarios borde: soft delete + create con mismo ID en otro tenant, list con filtros + deleted_at combinados

## 10. Configuración y dependencias

- [x] 10.1 Añadir `openpyxl` a `backend/pyproject.toml`
- [x] 10.2 Añadir `tenacity` a `backend/pyproject.toml` (para retry de Moodle WS)
- [x] 10.3 Añadir config vars: MOODLE_WS_TIMEOUT, MOODLE_WS_MAX_RETRIES en `core/config.py`
- [x] 10.4 Registrar permiso `padron:importar` en seed/migration de permisos (si existe)

## 11. Verificación final

- [x] 11.1 Ejecutar suite completa de tests (`pytest`) y confirmar verde (sin romper tests existentes de C-01 a C-07)
- [x] 11.2 Verificar `alembic upgrade head` y `alembic downgrade -1`
- [x] 11.3 Confirmar que ningún archivo `.py` supera 500 LOC
- [x] 11.4 Confirmar que todos los Pydantic schemas nuevos usan `extra='forbid'`
- [x] 11.5 Confirmar que no hay hard delete en ningún repository
- [x] 11.6 Confirmar que `email_encrypted` usa EncryptedField (AES-256) y no texto plano
- [x] 11.7 Confirmar que `EntradaPadron.usuario_id` es nullable (alumno sin cuenta)
