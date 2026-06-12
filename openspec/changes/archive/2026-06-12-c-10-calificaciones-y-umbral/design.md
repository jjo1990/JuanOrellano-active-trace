## Context

C-09 implementó el padrón versionado con `VersionPadron` y `EntradaPadron`. Ahora necesitamos calificaciones asociadas a esas entradas para poder detectar atrasados (C-11) y comunicar estados (C-12). El sistema debe soportar dos orígenes de calificaciones: importadas desde LMS (xlsx/csv) y manuales. Además, cada asignación docente puede tener umbrales de aprobación distintos para la misma materia.

Las reglas de negocio clave:
- **RN-01**: Columnas que terminan en "(Real)" son nota numérica.
- **RN-02**: "Satisfactorio" y "Supera lo esperado" cuentan como aprobado en notas textuales.
- **RN-03**: Umbral default de aprobación: 60%.

## Goals / Non-Goals

**Goals:**

- Modelos `Calificacion` y `UmbralMateria` con SQLAlchemy 2.0 async, siguiendo `BaseModelMixin`, soft delete, tenant isolation.
- `Calificacion.aprobado` es derivado (NO almacenado en BD): se calcula en service layer según umbral de la materia.
- `Calificacion.origen` es enum con CheckConstraint: `'Importado' | 'Manual'`.
- `UmbralMateria` con UniqueConstraint `(asignacion_id, materia_id, tenant_id)`. Scoped por asignación.
- Pipeline de import de calificaciones desde archivo: `POST /api/calificaciones/import` (upload + parse + detect columns + preview → token) → `POST /api/calificaciones/confirm/<token>` (persist).
- Pipeline de import de finalización (F1.2): `POST /api/calificaciones/import-finalizacion`.
- CRUD de umbrales: `GET /api/calificaciones/umbral/<materia_id>` y `PUT /api/calificaciones/umbral/<materia_id>`.
- Permiso `calificaciones:importar` con audit action `CALIFICACIONES_IMPORTAR`.
- Migración 010: tablas `calificacion` y `umbral_materia` con índices, FK y constraints.
- Tests: import xlsx/csv con detección RN-01/RN-02, umbral CRUD, aprobado derivado, tenant isolation.

**Non-Goals:**

- Detección de atrasados (→ C-11).
- Comunicaciones (→ C-12).
- Frontend de calificaciones (→ C-23).
- Integración Moodle WS para calificaciones (→ C-09 ya tiene MoodleClient.get_grades, se extiende si es necesario en otro change).

## Decisions

### D1 — `aprobado` es campo DERIVADO, no almacenado

`Calificacion` NO tiene columna `aprobado`. Se calcula en `CalificacionesService._es_aprobado(calificacion, umbral)`:

```
def _es_aprobado(cal: Calificacion, umbral: UmbralMateria | None) -> bool:
    if cal.nota_numerica is not None:
        pct = umbral.umbral_pct if umbral else 60  # RN-03 default
        return cal.nota_numerica >= pct
    if cal.nota_textual:
        valores = umbral.valores_aprobatorios if umbral else ["Satisfactorio", "Supera lo esperado"]
        return cal.nota_textual in valores
    return False
```

**Alternativa descartada**: almacenar `aprobado` como columna. Se descarta porque violaría el principio de single source of truth — si cambia el umbral, las calificaciones existentes quedarían inconsistentes. Además, el audit trail exige que el cálculo se haga siempre contra el umbral vigente.

### D2 — Cache de preview en memoria (mismo patrón que C-09)

Igual que en PadronService, la preview de import se guarda en un `dict` en memoria con TTL de 30 minutos. El token es un UUID.

**Alternativa descartada**: Redis. Se descarta para MVP por simplicidad y consistencia con C-09. Se migra a Redis si se necesita escalar.

### D3 — Un solo CalificacionesRepository

Se implementa un `CalificacionesRepository` que maneja `Calificacion` y `UmbralMateria`. Internamente usa dos `Repository[T]` genéricos. Esto simplifica transacciones donde se necesitan ambos modelos (ej: calcular aprobado requiere umbral).

### D4 — UmbralMateria scoped por asignación, no global por materia

Cada docente puede tener umbrales distintos para la misma materia. La asignación (asignacion_id) identifica qué docente/configuración aplica. Si no existe `UmbralMateria` para la asignación+materia, se usa el default 60% (RN-03).

**Alternativa descartada**: umbral global por materia. Se descarta porque diferentes docentes pueden tener criterios de evaluación distintos para la misma materia (ej: diferentes comisiones).

### D5 — Detección de columnas RN-01/RN-02 en service layer

Al parsear el archivo:
- Columnas cuyo nombre termina en "(Real)" → se marcan como nota numérica.
- Columnas cuyo nombre es "Satisfactorio" o "Supera lo esperado" → se muestran como textuales aprobatorias.
- El resto de columnas de actividad se muestran para que el usuario seleccione cuáles importar.

Esto ocurre en `CalificacionesService._detect_column_types()` y se devuelve en el preview para que el frontend permita selección.

### D6 — Layout de archivos nuevos/modificados

```
backend/app/
├── models/
│   ├── __init__.py                   # ✅ MODIFICADO: exporta Calificacion, UmbralMateria
│   ├── calificacion.py               # 🆕 Modelo Calificacion SQLAlchemy
│   └── umbral_materia.py             # 🆕 Modelo UmbralMateria SQLAlchemy
├── repositories/
│   ├── __init__.py                   # ✅ MODIFICADO
│   └── calificaciones_repository.py  # 🆕 CalificacionesRepository
├── services/
│   ├── __init__.py                   # ✅ MODIFICADO
│   └── calificaciones_service.py     # 🆕 CalificacionesService
├── schemas/
│   └── calificaciones.py             # 🆕 Pydantic schemas
├── api/v1/routers/
│   ├── __init__.py                   # ✅ MODIFICADO
│   └── calificaciones.py             # 🆕 Router
├── alembic/versions/
│   └── 010_create_calificacion_umbral.py  # 🆕 Migración
└── tests/
    ├── test_calificaciones_modelos.py      # 🆕 Tests modelos
    ├── test_calificaciones_import.py       # 🆕 Tests import xlsx/csv
    ├── test_calificaciones_umbral.py       # 🆕 Tests umbral CRUD
    └── test_calificaciones_tenant.py       # 🆕 Tests tenant isolation
```

### D7 — API Endpoints

| Método | Ruta | Auth | Permiso | Descripción |
|--------|------|------|---------|-------------|
| `POST` | `/api/calificaciones/import` | JWT | `calificaciones:importar` | Upload archivo, parsea, detecta columnas, retorna preview con token |
| `POST` | `/api/calificaciones/confirm/<preview_token>` | JWT | `calificaciones:importar` | Confirma preview, persiste Calificaciones contra EntradaPadron existente |
| `POST` | `/api/calificaciones/import-finalizacion` | JWT | `calificaciones:importar` | Importa reporte de finalización (F1.2) |
| `GET` | `/api/calificaciones/umbral/<materia_id>` | JWT | `calificaciones:importar` | Obtiene umbral de materia (scoped por asignación) |
| `PUT` | `/api/calificaciones/umbral/<materia_id>` | JWT | `calificaciones:importar` | Actualiza/crea umbral de materia |

Request `POST /api/calificaciones/import`:
- Body: `multipart/form-data` con `file` (archivo), `materia_id` (UUID), `cohorte_id` (UUID), `asignacion_id` (UUID).
- Detecta formato por extensión (.xlsx vs .csv).
- Detecta columnas: numéricas (terminan en "(Real)"), textuales aprobatorias ("Satisfactorio", "Supera lo esperado").
- Retorna: `{ preview_token, filename, detected_rows, columns: [{name, type, aprobatorio}], actividades: [{name, tipo, valores_ejemplo}], preview_rows: [...] }`.

Response `POST /api/calificaciones/confirm/<token>`:
- Body: `{ actividades_seleccionadas: string[] }` — columnas de actividad a importar.
- Retorna: `{ calificaciones_count, materia_id, cohorte_id, importado_at }`.

### D8 — Model Schemas

**Calificacion** (tabla `calificacion`):
- `id`: UUID PK
- `tenant_id`: UUID FK → tenant.id, NOT NULL
- `entrada_padron_id`: UUID FK → entrada_padron.id, NOT NULL
- `materia_id`: UUID FK → materia.id, NOT NULL
- `actividad`: String(200), NOT NULL — nombre de la actividad evaluable
- `nota_numerica`: Numeric(5,2), NULLABLE — valor numérico (nulo si solo textual)
- `nota_textual`: String(200), NULLABLE — descripción cualitativa
- `origen`: String(20), NOT NULL — CheckConstraint: `IN ('Importado', 'Manual')`
- `importado_at`: TIMESTAMP(timezone=True), server_default=func.now(), NOT NULL

**UmbralMateria** (tabla `umbral_materia`):
- `id`: UUID PK
- `tenant_id`: UUID FK → tenant.id, NOT NULL
- `asignacion_id`: UUID FK → asignacion.id, NOT NULL
- `materia_id`: UUID FK → materia.id, NOT NULL
- `umbral_pct`: Integer, NOT NULL, default=60
- `valores_aprobatorios`: JSONB, NOT NULL, default=["Satisfactorio", "Supera lo esperado"]
- UniqueConstraint: `(asignacion_id, materia_id, tenant_id)`

## Risks / Trade-offs

- **[Preview en memoria se pierde al reiniciar el servidor]** → Mitigación: mismo approach que C-09, aceptable para MVP. TTL 30 min.
- **[Archivos xlsx grandes (>10K filas) pueden ser lentos]** → Mitigación: usar `openpyxl read_only=True` (ya implementado en C-09). El volumen esperado de calificaciones por materia es manejable (cientos a miles de actividades × decenas de alumnos).
- **[Umbral por asignación puede llevar a configuraciones huérfanas si se elimina una asignación]** → Mitigación: soft delete. Si la asignación se elimina lógicamente, el umbral persiste para mantener el histórico. Se puede limpiar si es necesario.
- **[aprobado derivado puede ser costoso si se lista muchas calificaciones]** → Mitigación: el cálculo es O(1) por calificación (solo requiere umbral de la materia, que se carga una vez). Si hay N calificaciones, es O(N) con un solo query de umbral. Si escala a millones, se agrega caché de umbral o columna derivada materializada con refresh controlado.
- **[Detección RN-01/RN-02 depende del naming de columnas del LMS]** → Mitigación: el preview muestra todas las columnas detectadas con su tipo inferido. El usuario puede corregir la clasificación antes de confirmar.

## Migration Plan

1. Generar migración 010 con `alembic revision --autogenerate` o manual.
2. Ejecutar `alembic upgrade head` contra base de desarrollo.
3. Verificar tablas, índices, FK y CheckConstraint.
4. Rollback: `alembic downgrade -1` elimina ambas tablas.

## Open Questions

- **¿Se necesita soportar drag-and-drop de columnas en preview?** Se asume que no para MVP; el usuario solo selecciona qué actividades importar de las detectadas.
- **¿El import de finalización (F1.2) es un endpoint separado o el mismo con flag?** Se diseña como endpoint separado (`/import-finalizacion`) porque la lógica de detección y persistencia es distinta (no busca columnas de nota, busca estado de finalización).
- **¿Qué pasa si no hay EntradaPadron activa para un alumno en el archivo?** Se omite ese registro y se reporta en el response como `ignorados`.
