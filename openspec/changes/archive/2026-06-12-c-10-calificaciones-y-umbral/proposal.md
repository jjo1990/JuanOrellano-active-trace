## Why

C-09 dejó el padrón de alumnos listo, pero sin calificaciones no se puede detectar atrasados (C-11) ni comunicar estados. C-10 agrega el modelo de calificaciones con importación desde archivos LMS, detección automática de aprobación vía umbrales configurables por materia, y el pipeline de preview+confirm que ya probamos en C-09.

## What Changes

- **Modelo Calificacion**: asociada a EntradaPadron, con nota_numerica (nullable), nota_textual (nullable), y origen enum (`Importado` | `Manual`). `aprobado` es un campo DERIVADO (no se almacena): se calcula en service layer según nota_numerica >= umbral_materia.umbral_pct o nota_textual in valores_aprobatorios.
- **Modelo UmbralMateria**: umbral_pct default 60, valores_aprobatorios (JSONB), UniqueConstraint por (asignacion_id, materia_id, tenant_id). Scoped por asignación: cada docente puede tener umbrales distintos para la misma materia.
- **Import de calificaciones desde archivo** (.xlsx/.csv): subida → parseo → detección de columnas por RN-01 (terminan en "(Real)" → numéricas) y RN-02 ("Satisfactorio"/"Supera lo esperado" → textuales aprobadas) → preview con selección de actividades → confirm → persist.
- **Import de reporte de finalización** (F1.2): archivos con entregas finalizadas sin calificación, almacena como Calificacion con nota_textual indicando estado.
- **CRUD de umbrales**: GET/PUT /api/calificaciones/umbral/<materia_id>, scoped por asignación.
- **Permiso**: `calificaciones:importar` (ya existe en action_codes como CALIFICACIONES_IMPORTAR).
- **Audit action**: `CALIFICACIONES_IMPORTAR` ya registrado en action_codes.py.
- **Migración 010**: tablas `calificacion`, `umbral_materia` con CheckConstraint en origen y UniqueConstraint en umbral.

## Capabilities

### New Capabilities

- `calificacion-model`: modelo Calificacion con nota_numerica/nota_textual, origen enum, aprobado derivado.
- `umbral-materia`: modelo UmbralMateria con umbral_pct y valores_aprobatorios JSONB, scoped por asignación.
- `import-calificaciones`: pipeline de import desde archivo .xlsx/.csv con detección de columnas RN-01/RN-02, preview y confirm.
- `import-finalizacion`: pipeline de import de reportes de finalización (F1.2).
- `umbral-crud`: endpoints GET/PUT para configurar umbral por materia, scoped por asignación.
- `migration-010`: migración Alembic que crea `calificacion` + `umbral_materia`.

### Modified Capabilities

- `app-scaffold` (C-01): se agregan dependencias necesarias para parseo de archivos (openpyxl ya está desde C-09).
- `rbac` (C-04): se registra permiso `calificaciones:importar` (si no existe aún en seed).

## Impact

- **Nuevo código**: `models/calificacion.py`, `models/umbral_materia.py`, `repositories/calificaciones_repository.py`, `services/calificaciones_service.py`, `schemas/calificaciones.py`, `routers/calificaciones.py`, tests.
- **Schema de BD**: migración 010 crea `calificacion` y `umbral_materia`.
- **Config**: registro del permiso `calificaciones:importar` en seed de permisos.
- **Dependencias**: openpyxl (ya desde C-09), csv (stdlib).
- **Habilita**: C-11 (atrasados) necesita calificaciones para detectar entregas pendientes.
- **Governance**: MEDIO — lógica de dominio con reglas de negocio RN-01/RN-02/RN-03.
