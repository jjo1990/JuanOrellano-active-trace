## Why

Sin un padrón de alumnos importado, el sistema no puede operar sobre calificaciones, atrasados ni comunicaciones. C-07 dejó usuarios y asignaciones listos, pero el dato base — qué alumnos cursan qué materia, en qué comisión y regional — todavía no existe. C-09 llena ese vacío con un sistema versionado de padrones que permite importar desde Moodle WS (automático) o desde archivos .xlsx/.csv (fallback manual), con preview antes de confirmar. Es el paso 1 del flujo FL-02 (importación → análisis → comunicación).

## What Changes

- **Modelos VersionPadron y EntradaPadron**: versión activa única por (materia, cohorte). Al activar una nueva, la anterior se desactiva (no se borra). EntradaPadron permite `usuario_id` nullable (alumno sin cuenta todavía).
- **Import de padrón desde archivo** (.xlsx via openpyxl, .csv via csv module): upload → parse → preview (retorna token) → confirm → persist. Upsert destructivo (RN-05): reemplaza completamente el padrón anterior de la materia.
- **Integración Moodle Web Services** (`integrations/moodle_ws.py`): cliente async para sync de usuarios/actividades, nightly sync + on-demand, errores mapean a 502 con retry.
- **Vaciar datos de materia** (F1.5, RN-04): elimina calificaciones e ingesta de una materia, scoped a `(usuario_id, materia_id)`.
- **Permiso**: `padron:importar`.
- **Audit action**: `PADRON_CARGAR`.
- **Migración 009**: tablas `version_padron`, `entrada_padron`.

## Capabilities

### New Capabilities

- `version-padron`: modelo VersionPadron con versionado (una activa por materia×cohorte, activar desactiva anterior).
- `entrada-padron`: modelo EntradaPadron con email cifrado, usuario_id nullable, desnormalizado para histórico.
- `import-file`: pipeline de importación desde archivo .xlsx/.csv con preview y confirmación.
- `moodle-ws-integration`: cliente async Moodle Web Services con sync de padrón, nightly cron y fallback 502.
- `vaciar-materia`: endpoint para eliminar datos de ingesta/calificaciones de una materia (RN-04).
- `migration-009`: migración Alembic que crea `version_padron` + `entrada_padron`.

### Modified Capabilities

- `audit-log` (C-05): se agrega action code `PADRON_CARGAR` a los valores conocidos de auditoría.
- `app-scaffold` (C-01): se agrega `openpyxl` a dependencias del proyecto.
- `rbac` (C-04): se registra el permiso `padron:importar` en la matriz de permisos.

## Impact

- **Nuevo código**: `models/version_padron.py`, `models/entrada_padron.py`, `repositories/padron_repository.py`, `services/padron_service.py`, `routers/padron.py`, `integrations/moodle_ws.py`, tests.
- **Schema de BD**: migración 009 crea `version_padron` y `entrada_padron`.
- **Config**: se añade `MOODLE_WS_*` vars a settings, `openpyxl` a `pyproject.toml`.
- **Dependencias**: `openpyxl` (lectura xlsx).
- **Habilita**: C-10 (calificaciones-y-umbral necesita padrón como entrada).
- **Governance**: MEDIO — cambios en dominio de negocio con integración externa.
