## Context

C-07 dejó el sistema con usuarios, roles, asignaciones y estructura académica. El modelo multi-tenant y RBAC ya operan. El próximo paso lógico del camino crítico es poblar el padrón de alumnos — sin él, las calificaciones (C-10) y el análisis de atrasados (C-11) no tienen datos sobre los que operar.

El flujo FL-02 define 2 caminos de ingesta:
- **Automático**: vía Moodle Web Services (tenants con WS configurado).
- **Fallback manual**: subida de archivo .xlsx/.csv con preview y confirmación.

Ambos caminos convergen en el mismo modelo versionado: `VersionPadron` (una activa por materia×cohorte) y `EntradaPadron` (registros individuales con email cifrado y usuario_id nullable).

## Goals / Non-Goals

**Goals:**

- Modelos `VersionPadron` y `EntradaPadron` con SQLAlchemy 2.0 async, siguiendo `BaseModelMixin`, con soft delete y tenant isolation.
- Lógica de versionado: al activar una nueva versión para (materia, cohorte), la anterior se desactiva (activa=False), nunca se borra.
- Pipeline de import desde archivo: `POST /api/padron/import` (upload + parse + preview → token) → `POST /api/padron/confirm/<token>` (persist). Usar openpyxl para .xlsx, csv module (con sniffing de dialecto) para .csv.
- Integración Moodle WS: cliente async en `integrations/moodle_ws.py`, sync on-demand + nightly cron, errores → 502 con retry programado.
- Endpoint `DELETE /api/padron/vaciar/<materia_id>` con soft delete de todas las entradas de la materia, scoped a rol PROFESOR (solo propias) y COORDINADOR (global).
- Permiso `padron:importar` registrado en RBAC.
- Audit action `PADRON_CARGAR` para import (confirm) y vaciar.
- Migration 009: tablas `version_padron`, `entrada_padron` con índices y FK.
- Tests: versionado (activar desactiva anterior), import xlsx/csv, entrada sin usuario_id (alumno sin cuenta), tenant isolation, mock Moodle WS + fallback 502.

**Non-Goals:**

- Import de calificaciones (→ C-10).
- Análisis de atrasados (→ C-11).
- Comunicaciones (→ C-12).
- Frontend de importación (→ C-22).
- Seed de datos ni migración de datos legacy.
- UI de preview (solo backend retorna datos; la UI se hace en frontend).

## Decisions

### D1 — Versionado con flag activa, no con DELETE cascade

Cada `VersionPadron` tiene un flag `activa: bool`. Al crear una nueva versión para el mismo par (materia, cohorte), el service setea `activa=False` en la anterior antes de persistir la nueva. Esto preserva el histórico completo: siempre se puede consultar versiones anteriores.

**Alternativa descartada**: eliminar la versión anterior y reemplazar. Se descarta porque viola el principio de auditoría append-only (soft delete siempre). Además, tener histórico permite revertir o comparar versiones.

**Alternativa descartada**: usar `deleted_at` en vez de `activa`. Se descarta porque una versión anterior no está "eliminada" — está inactiva pero disponible para consulta. Soft delete es para eliminación lógica, no para desactivación.

### D2 — Preview efímera con token en memoria/cache

El import en 2 pasos funciona así:
1. `POST /api/padron/import` — upload archivo → parse → guarda preview en caché (Redis o dict en memoria para MVP) con un token UUID → retorna token con resumen y primeras filas.
2. `POST /api/padron/confirm/<token>` — busca preview por token → si expiró (>30 min) retorna 404 → si válido, persiste VersionPadron + EntradaPadron → invalida token.

Para MVP la preview se guarda en un `dict` en memoria (simple). En producción se migra a Redis.

**Alternativa descartada**: subir y persistir inmediatamente sin preview. Se descarta porque el usuario necesita ver qué se va a importar antes de confirmar (F1.3 lo exige).

### D3 — Cliente Moodle WS como módulo independiente

`integrations/moodle_ws.py` encapsula toda la lógica de comunicación con Moodle:
- `MoodleClient` clase async con `__init__(base_url, token)`.
- Métodos: `get_enrolled_users(course_id)`, `get_activities(course_id)`, `get_grades(...)`.
- Usa `httpx.AsyncClient` para requests HTTP.
- Manejo de errores: timeouts, connexion refused, HTTP errors → todos mapean a `MoodleWSException` → 502.
- Retry con exponential backoff: 3 intentos (1s, 5s, 15s).

La configuración por tenant (WS URL + token) se almacena en `tenant.config["moodle"]` (JSONB).

**Alternativa descartada**: meter la lógica Moodle dentro de un servicio. Se descarta por separación de concerns: `services/padron_service.py` usa `MoodleClient` como dependencia, no contiene lógica HTTP.

### D4 — Email cifrado en EntradaPadron

Siguiendo el patrón de `user.py`, el email en `EntradaPadron` se almacena cifrado vía `EncryptedField` + columna `email_encrypted`. Esto protege PII. Los demás campos (nombre, apellidos, comision, regional) se almacenan en texto plano (no son PII sensible).

**Alternativa descartada**: no cifrar email. Se descarta porque el email es PII identificable y el sistema ya estableció que todo `[cifrado]` va con AES-256 vía EncryptedField.

### D5 — Un único PadronRepository, no dos

Aunque hay dos modelos, se implementa un solo `PadronRepository` que maneja VersionPadron y EntradaPadron. Esto simplifica las transacciones (crear versión + entradas es una unidad). Internamente usa el `Repository[T]` genérico.

### D6 — Layout de archivos nuevos/modificados

```
backend/app/
├── models/
│   ├── __init__.py                   # ✅ MODIFICADO: exporta VersionPadron, EntradaPadron
│   ├── version_padron.py             # 🆕 Modelo VersionPadron SQLAlchemy
│   └── entrada_padron.py             # 🆕 Modelo EntradaPadron SQLAlchemy
├── repositories/
│   ├── __init__.py                   # ✅ MODIFICADO
│   └── padron_repository.py          # 🆕 PadronRepository (versionado + entradas)
├── services/
│   ├── __init__.py                   # ✅ MODIFICADO
│   └── padron_service.py             # 🆕 PadronService (import, confirm, vaciar, sync moodle)
├── routers/
│   ├── __init__.py                   # ✅ MODIFICADO
│   └── padron.py                     # 🆕 Router (import, confirm, vaciar)
├── integrations/
│   ├── __init__.py                   # 🆕 (crear si no existe)
│   └── moodle_ws.py                  # 🆕 MoodleClient async
├── workers/
│   ├── __init__.py                   # ✅ MODIFICADO (si existe)
│   └── nightly_sync.py               # 🆕 Worker de sync nocturna
├── alembic/
│   └── versions/
│       └── 009_create_version_padron_entrada.py  # 🆕 Migración
├── schemas/
│   ├── padron.py                     # 🆕 Pydantic schemas (VersionPadronDTO, EntradaPadronDTO, PreviewResponse, etc.)
│   └── audit.py                      # ✅ MODIFICADO: se agrega PADRON_CARGAR
└── tests/
    ├── test_padron_versionado.py     # 🆕 Test versionado
    ├── test_padron_import.py         # 🆕 Test import xlsx/csv
    ├── test_padron_vaciar.py         # 🆕 Test vaciar materia
    ├── test_padron_tenant.py         # 🆕 Test tenant isolation
    └── test_moodle_ws.py             # 🆕 Test moodle WS (mock)
```

### D7 — API Endpoints

| Método | Ruta | Auth | Permiso | Descripción |
|--------|------|------|---------|-------------|
| `POST` | `/api/padron/import` | JWT | `padron:importar` | Upload archivo, parsea, retorna preview token |
| `POST` | `/api/padron/confirm/<preview_token>` | JWT | `padron:importar` | Confirma preview, persiste versión + entradas |
| `DELETE` | `/api/padron/vaciar/<materia_id>` | JWT | `padron:importar` | Soft delete de datos de materia |
| `POST` | `/api/padron/sync-moodle/<materia_id>` | JWT | `padron:importar` | Sync on-demand desde Moodle WS |

Request `POST /api/padron/import`:
- Body: `multipart/form-data` con `file` (archivo), `materia_id` (UUID), `cohorte_id` (UUID).
- Detecta formato por extensión (.xlsx vs .csv).
- Retorna: `{ preview_token, filename, detected_rows, columns, preview_rows: [...] }`.

Response `POST /api/padron/confirm/<token>`:
- Retorna: `{ version_id, entries_count, materia_id, cohorte_id, cargado_at }`.

## Risks / Trade-offs

- **[Preview en memoria se pierde al reiniciar el servidor]** → Mitigación: para MVP es aceptable; el usuario re-subiría el archivo. En producción se usa Redis. El TTL de 30 min minimiza el impacto.
- **[openpyxl es lento con archivos muy grandes (>100K filas)]** → Mitigación: el volumen esperado por materia es de decenas a cientos de alumnos, no miles. Si se necesita escalar, se evalúa procesamiento en stream con `openpyxl.read_only=True` o chunked.
- **[Moodle WS puede tener rate limiting]** → Mitigación: el cliente implementa retry con backoff. Si hay rate limiting severo, se agrega throttling en el cliente (1 request por segundo). Se documenta en configuración del tenant.
- **[Email cifrado impide búsqueda por email exacto]** → Mitigación: no se necesita búsqueda por email en este módulo. Si se requiere en el futuro, se agrega un hash SHA-256 del email en texto plano como columna de índice (no reversible).
- **[Vaciar materia es irreversible (soft-delete)]** → Mitigación: soft delete permite restaurar si es necesario vía DB directa o un futuro endpoint de restore. El audit log registra quién y cuándo.

## Migration Plan

1. Generar migración 009 con `alembic revision --autogenerate` o manual.
2. Ejecutar `alembic upgrade head` contra la base de desarrollo.
3. Verificar que las tablas se crean con los índices y FK correctos.
4. Rollback: `alembic downgrade -1` elimina ambas tablas (sin pérdida de datos de negocio porque no hay datos reales todavía).

## Open Questions

- **¿TTL de preview token?** Se propone 30 minutos. ¿Debería ser configurable por tenant? Decisión: fijo por ahora, se parametriza si se solicita.
- **¿Columnas requeridas en el archivo de import?** Mínimo: nombre, apellidos, email. Comision y regional son opcionales. Confirmar si hay columnas adicionales del negocio.
- **¿Moodle WS soporta `core_enrol_get_enrolled_users` con filtro por curso?** Sí, es el endpoint estándar. Pero necesita confirmación sobre qué endpoint específico usa cada institución. Se asume endpoint estándar de Moodle 4.x.
