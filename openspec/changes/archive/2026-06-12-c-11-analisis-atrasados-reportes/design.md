## Context

C-10 entregó `Calificacion` y `UmbralMateria` con su ingesta completa. C-11 construye la capa de análisis puramente computacional sobre esos datos. No hay nuevas tablas ni migraciones. El `AnalisisService` consume datos de `CalificacionesRepository` y `PadronRepository` y devuelve resultados computados en Python.

El flujo central del PROFESOR (FL-02, pasos 5-6) depende de este change para cerrar el ciclo importar → analizar. Los endpoints exponen las funcionalidades F2.2 a F2.9 de la Épica 2.

**Constraints:**
- snake_case en todo Python
- Pydantic v2 con `extra='forbid'`
- Identidad desde sesión JWT, tenant desde `user.tenant_id`
- `atrasados:ver` como permiso nuevo
- Sin lógica de negocio en routers, sin SQL directo en services
- ≤500 LOC por archivo backend

## Goals / Non-Goals

**Goals:**

- Servicio `AnalisisService` con métodos de cómputo puro (algoritmos en Python, queries vía repositorios existentes).
- 8 endpoints GET en `/api/analisis/*` con guard `atrasados:ver`.
- Schemas de respuesta tipados con `extra='forbid'` para cada endpoint.
- Atrasados: detectar alumnos con actividades faltantes o nota < umbral (RN-06).
- Ranking: contar aprobadas por alumno, filtrar ≥1, ordenar descendente (RN-09).
- Reportes rápidos: métricas consolidadas por materia.
- Notas finales: agrupación por alumno con nota final.
- TPs sin corregir: cruce reporte finalización vs calificaciones, solo escala textual (RN-07, RN-08).
- Monitor general: filtros por materia, regional, comision, alumno, estado (F2.7).
- Monitor seguimiento: vista filtrable por docente (F2.8).
- Monitor admin: extiende seguimiento con rango de fechas (F2.9).
- Tests con DB real para cada algoritmo de cómputo y tenant isolation.
- Action code `ANALISIS_CONSULTAR` para auditoría.

**Non-Goals:**

- Migración de base de datos (no hay modelos nuevos).
- Comunicaciones a atrasados (→ C-12).
- Export de archivos descargables (se implementa el cómputo; la exportación real puede ser frontend puro con los datos del endpoint).
- Modificación de calificaciones o umbrales desde estos endpoints (eso es C-10).
- Frontend de análisis (→ C-22).
- Caché o Redis (MVP no lo requiere; cada materia tiene <1000 calificaciones típicamente).

## Decisions

### D1 — Lógica de cómputo en Python, no en SQL

Todo el análisis (atrasados, ranking, agrupación, cruce) se implementa en `AnalisisService` con iteraciones sobre los datos cargados desde repositorios. No se usan window functions, CTEs complejas ni queries analíticas.

**Rationale:** Las materias tienen típicamente <1000 calificaciones. Cargar todo a memoria y computar en Python es más legible, testeable y mantenible que SQL complejo. Además, cumple la regla "sin SQL en Services" — los services orquestan datos de repositorios y aplican lógica en Python.

**Alternativa descartada:** queries analíticas en PostgreSQL. Se descarta porque el volumen no lo justifica y la testabilidad de la lógica en Python es superior.

### D2 — AnalisisService recibe CalificacionesRepository + PadronRepository

El constructor inyecta ambos repositorios (ya existentes). No se crea un repositorio nuevo.

```python
class AnalisisService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID) -> None:
        self._cal_repo = CalificacionesRepository(session, tenant_id)
        self._padron_repo = PadronRepository(session, tenant_id)
        self._session = session
        self._tenant_id = tenant_id
```

**Rationale:** C-11 no persiste nada. Reutiliza los repositorios existentes que ya manejan scope tenant y soft delete.

### D3 — Umbral por defecto cuando no está configurado

Cuando no existe `UmbralMateria` para una materia, se usa `umbral_pct=60` y `valores_aprobatorios=["Satisfactorio", "Supera lo esperado"]`. Esto replica la lógica ya implementada en `CalificacionesService._es_aprobado()`.

**Rationale:** Consistencia con C-10. RN-03 define el default del 60%.

### D4 — Algoritmo de "atrasado" (RN-06)

Para una materia dada:
1. Obtener todas las `EntradaPadron` activas del padrón vigente de la materia.
2. Obtener todas las `Calificacion` de esa materia.
3. Obtener todas las actividades distintas presentes en las calificaciones de la materia (el "universo" de actividades).
4. Obtener el `UmbralMateria` configurado (o defaults).
5. Para cada alumno (EntradaPadron):
   - `actividades_presentes` = set de actividades con calificación del alumno.
   - `actividades_faltantes` = universo - actividades_presentes.
   - `nota_baja` = alguna calificación con nota < umbral (según `_es_aprobado`).
   - `atrasado` = faltantes > 0 OR nota_baja.

Un alumno **sin calificaciones** en absoluto es atrasado (todas las actividades son faltantes).

### D5 — Ranking excluye alumnos sin aprobadas (RN-09)

Para cada alumno, contar `len([c for c in calificaciones if _es_aprobado(c, umbral)])`. Filtrar los que tienen count == 0. Ordenar descendente por count.

### D6 — TPs sin corregir recibe reporte de finalización como input

El endpoint `GET /api/analisis/sin-corregir/{materia_id}` recibe un `reporte_finalizacion_id` como query param que referencia un reporte previamente importado en C-10 (`ImportFinalizacionResponse`). El servicio:
1. Carga el reporte de finalización desde la sesión de preview cache o desde un almacenamiento persistente (según cómo se implementó en C-10).
2. Filtra SOLO actividades de escala textual (RN-08).
3. Cruza: alumno completó la actividad en el reporte pero NO tiene calificación en `Calificacion`.
4. Devuelve el listado de (alumno, actividad) sin corregir.

**Alternativa considerada:** recibir el archivo de finalización directamente en este endpoint. Se descarta porque ya existe el pipeline de import en C-10 y reusar ese token es más consistente.

### D7 — Monitor usa joins vía repositorios

El monitor general carga todas las calificaciones y entradas de padrón, y filtra en Python por los query params: `materia_id`, `regional`, `comision`, `alumno_nombre`, `estado` (atrasado/al-dia/aprobado). El filtrado en Python sobre datasets chicos es más simple y testeable que queries dinámicas complejas.

### D8 — Estructura de endpoints

Todos bajo un solo router `APIRouter(prefix="/api/analisis", tags=["analisis"])`. Cada endpoint usa `Depends(require_permission("atrasados:ver"))`. Los paths siguen el patrón REST:

| Método | Path | Descripción |
|--------|------|-------------|
| GET | `/api/analisis/atrasados/{materia_id}` | Alumnos atrasados |
| GET | `/api/analisis/ranking/{materia_id}` | Ranking actividades aprobadas |
| GET | `/api/analisis/reportes/{materia_id}` | Reportes rápidos |
| GET | `/api/analisis/notas-finales/{materia_id}` | Notas finales agrupadas |
| GET | `/api/analisis/sin-corregir/{materia_id}` | TPs sin corregir |
| GET | `/api/analisis/monitor` | Monitor general |
| GET | `/api/analisis/monitor/seguimiento` | Monitor seguimiento |
| GET | `/api/analisis/monitor/admin` | Monitor admin (rango fechas) |

## Risks / Trade-offs

- **[Riesgo] Carga completa en memoria para materias grandes (>10k alumnos)** → **Mitigación**: para MVP el volumen es bajo. Si escala, se puede paginar o mover a queries SQL. Se deja documentado como deuda técnica.
- **[Riesgo] Reporte de finalización almacenado en preview cache con TTL de 30 min** → **Mitigación**: el usuario debe tener el token fresco. Si se necesita persistencia, se puede migrar a tabla en change futuro.
- **[Riesgo] Sin paginación en monitores** → **Mitigación**: los filtros reducen el dataset. Se puede agregar paginación en iteración futura si el volumen lo requiere.
- **[Trade-off] Cómputo en Python vs SQL**: legibilidad y testabilidad a cambio de posible overhead en datasets grandes. Aceptable para MVP.
