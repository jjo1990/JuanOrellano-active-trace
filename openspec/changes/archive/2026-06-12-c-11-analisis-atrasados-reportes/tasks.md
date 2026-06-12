## 1. Schemas — Response DTOs

- [x] 1.1 Create `backend/app/schemas/analisis.py` with `model_config = ConfigDict(extra='forbid')` on all schemas
- [x] 1.2 Implement `NotaBajaDTO` (actividad: str, nota: float|null, nota_textual: str|null) and `AlumnoAtrasadoDTO` (entrada_padron_id, nombre, apellidos, email, comision, regional, actividades_faltantes: list[str], notas_bajas: list[NotaBajaDTO])
- [x] 1.3 Implement `AtrasadosResponse` (materia_id, total_alumnos, total_atrasados, atrasados: list[AlumnoAtrasadoDTO], status_info: str|null)
- [x] 1.4 Implement `RankingEntryDTO` (entrada_padron_id, nombre, apellidos, email, comision, regional, total_actividades, aprobadas, porcentaje) and `RankingResponse` (materia_id, total_alumnos, ranking: list[RankingEntryDTO], status_info: str|null)
- [x] 1.5 Implement `ReportesResponse` (materia_id, total_alumnos, total_actividades, aprobacion_general: float, distribucion_notas: dict[str,int], alumnos_al_dia, alumnos_atrasados, actividad_mas_dificil: str|null, actividad_mas_facil: str|null, status_info: str|null)
- [x] 1.6 Implement `NotaFinalDTO` (entrada_padron_id, nombre, apellidos, email, comision, regional, nota_final: float|null, aprobado_final: bool, calificaciones: list[CalificacionDTO]) and `NotasFinalesResponse` (materia_id, notas: list[NotaFinalDTO], status_info: str|null)
- [x] 1.7 Implement `EntregaSinCorregirDTO` (entrada_padron_id, nombre, apellidos, email, comision, actividad, fecha_finalizacion) and `SinCorregirResponse` (materia_id, total_sin_corregir, entregas: list[EntregaSinCorregirDTO])
- [x] 1.8 Implement `MonitorEntryDTO` (entrada_padron_id, nombre, apellidos, email, materia_id, materia_nombre, comision, regional, estado: str, total_actividades, aprobadas, faltantes, ultima_actividad: str|null) and `MonitorResponse` (total, estudiantes: list[MonitorEntryDTO])
- [x] 1.9 Implement `SeguimientoEntryDTO` and `SeguimientoResponse` (same as MonitorEntryDTO minus ultima_actividad)
- [x] 1.10 Implement `AdminMonitorEntryDTO` and `AdminMonitorResponse` (extends Seguimiento with rango_fechas: {desde, hasta}|null)

## 2. Config — Action Code y Permiso

- [x] 2.1 Add `ANALISIS_CONSULTAR = "ANALISIS_CONSULTAR"` to `backend/app/core/action_codes.py`
- [x] 2.2 Add seed for permission `atrasados:ver` in `backend/app/core/permissions.py` (or wherever the permission seed logic lives; verify against existing patterns for `calificaciones:importar`)
- [x] 2.3 Verify the new permission is registered in the seed script or migration (check if there's a seed file like `backend/app/core/seed.py` or similar)

## 3. AnalisisService — Core Computation

- [x] 3.1 Create `backend/app/services/analisis_service.py` with class `AnalisisService(session, tenant_id)` injecting `CalificacionesRepository` and `PadronRepository`
- [x] 3.2 Implement `_get_umbral(materia_id) -> dict` that loads `UmbralMateria` or returns defaults `{umbral_pct: 60, valores_aprobatorios: ["Satisfactorio", "Supera lo esperado"]}`
- [x] 3.3 Implement `_es_aprobado(calificacion, umbral) -> bool` reusing the same logic from `CalificacionesService._es_aprobado()` (numeric >= umbral_pct, textual in valores_aprobatorios)
- [x] 3.4 Implement `_get_actividades_universo(materia_id) -> set[str]` that returns all distinct actividad names from calificaciones of that materia
- [x] 3.5 Implement `compute_atrasados(materia_id) -> AtrasadosResponse` following RN-06: iterate all EntradaPadron in active padrón, check faltantes + nota baja, build response
- [x] 3.6 Implement `compute_ranking(materia_id) -> RankingResponse` following RN-09: count approved per student, filter >=1, sort desc
- [x] 3.7 Implement `compute_reportes(materia_id) -> ReportesResponse` with all aggregated metrics (total_alumnos, distribucion_notas, hardest/easiest activity)
- [x] 3.8 Implement `compute_notas_finales(materia_id) -> NotasFinalesResponse` with grouped calificaciones per student, nota_final average, aprobado_final flag
- [x] 3.9 Implement `compute_sin_corregir(materia_id, reporte_token) -> SinCorregirResponse` loading finalization report from preview cache, filtering textual-scale only (RN-08), crossing with calificaciones (RN-07)
- [x] 3.10 Implement `compute_monitor(filtros: MonitorFilterParams) -> MonitorResponse` with optional filters (materia_id, regional, comision, alumno, estado) applying all filters in Python
- [x] 3.11 Implement `compute_monitor_seguimiento(filtros: SeguimientoFilterParams, usuario_id) -> SeguimientoResponse` scoping to the teacher's asignaciones and applying filters
- [x] 3.12 Implement `compute_monitor_admin(filtros: AdminMonitorFilterParams) -> AdminMonitorResponse` with date range filter on `importado_at`
- [x] 3.13 Implement `_resolve_estado(entrada, calificaciones, umbral, universo) -> str` returning "atrasado", "al_dia", or "aprobado_todos" for monitor endpoints
- [x] 3.14 Add logging and audit calls using `action_codes.ANALISIS_CONSULTAR` (check if audit middleware is automatic or needs explicit calls in the service)

## 4. Router — /api/analisis/* Endpoints

- [x] 4.1 Create `backend/app/api/v1/routers/analisis.py` with `APIRouter(prefix="/api/analisis", tags=["analisis"])`
- [x] 4.2 Implement `GET /api/analisis/atrasados/{materia_id}` with `require_permission("atrasados:ver")`, calling `AnalisisService.compute_atrasados(materia_id)`
- [x] 4.3 Implement `GET /api/analisis/ranking/{materia_id}` with `require_permission("atrasados:ver")`, calling `compute_ranking`
- [x] 4.4 Implement `GET /api/analisis/reportes/{materia_id}` with `require_permission("atrasados:ver")`, calling `compute_reportes`
- [x] 4.5 Implement `GET /api/analisis/notas-finales/{materia_id}` with `require_permission("atrasados:ver")`, calling `compute_notas_finales`
- [x] 4.6 Implement `GET /api/analisis/sin-corregir/{materia_id}` with query param `reporte_token: str`, calling `compute_sin_corregir`
- [x] 4.7 Implement `GET /api/analisis/monitor` with optional query params (materia_id, regional, comision, alumno, estado), calling `compute_monitor`
- [x] 4.8 Implement `GET /api/analisis/monitor/seguimiento` with optional query params (alumno, comision, regional, actividad, min_aprobadas) + scoped to authenticated user's asignaciones
- [x] 4.9 Implement `GET /api/analisis/monitor/admin` with optional query params (materia_id, regional, comision, alumno, estado, fecha_desde, fecha_hasta), calling `compute_monitor_admin`
- [x] 4.10 Register the new router in `backend/app/api/v1/__init__.py` or `backend/app/main.py` (check how existing routers like `calificaciones` are registered)

## 5. Tests — Atrasados

- [x] 5.1 Create `backend/tests/test_analisis_atrasados.py` with fixtures for materia, entradas_padron, calificaciones, umbral
- [x] 5.2 Test: student with missing activities is flagged as atrasado
- [x] 5.3 Test: student with nota below umbral is flagged as atrasado
- [x] 5.4 Test: student with nota_textual not in approved values is flagged as atrasado
- [x] 5.5 Test: student with zero calificaciones is atrasado (all activities missing)
- [x] 5.6 Test: student al dia (all activities present, all notas >= umbral) is NOT in atrasados
- [x] 5.7 Test: materia with no calificaciones returns empty list with status_info
- [x] 5.8 Test: uses default umbral when no UmbralMateria configured
- [x] 5.9 Test: tenant isolation — only tenant A's data returned when tenant A and B have entries

## 6. Tests — Ranking

- [x] 6.1 Create `backend/tests/test_analisis_ranking.py`
- [x] 6.2 Test: ranking returns students ordered by approved count descending
- [x] 6.3 Test: student with 0 approved activities is excluded from ranking
- [x] 6.4 Test: all students excluded when none have approved activities (empty ranking + status_info)
- [x] 6.5 Test: textual nota "Satisfactorio" counts as approved
- [x] 6.6 Test: default umbral applies when not configured (60%)
- [x] 6.7 Test: tenant isolation

## 7. Tests — Reportes

- [x] 7.1 Create `backend/tests/test_analisis_reportes.py`
- [x] 7.2 Test: reportes returns correct metrics for materia with varied calificaciones
- [x] 7.3 Test: materia with no calificaciones returns all zeros with status_info
- [x] 7.4 Test: actividad_mas_dificil and actividad_mas_facil computed correctly
- [x] 7.5 Test: distribucion_notas buckets work correctly
- [x] 7.6 Test: tenant isolation

## 8. Tests — Monitor (general, seguimiento, admin)

- [x] 8.1 Create `backend/tests/test_analisis_monitor.py`
- [x] 8.2 Test: monitor-general returns all students across tenant
- [x] 8.3 Test: monitor-general filters by materia_id
- [x] 8.4 Test: monitor-general filters by regional
- [x] 8.5 Test: monitor-general filters by estado (atrasado/al_dia/aprobado_todos)
- [x] 8.6 Test: monitor-general free-text search by alumno name
- [x] 8.7 Test: monitor-general combined filters work correctly
- [x] 8.8 Test: monitor-seguimiento only returns students from teacher's asignaciones
- [x] 8.9 Test: monitor-seguimiento filters by min_aprobadas
- [x] 8.10 Test: monitor-seguimiento filters by actividad name
- [x] 8.11 Test: monitor-admin with fecha_desde/fecha_hasta filters calificaciones by importado_at
- [x] 8.12 Test: monitor-admin without date range behaves like monitor-general
- [x] 8.13 Test: nota_finales endpoint groups correctly with mixed numeric/textual
- [x] 8.14 Test: sin-corregir endpoint returns ungraded textual-only activities from finalization report
- [x] 8.15 Test: sin-corregir returns 404 on expired/invalid reporte_token
- [x] 8.16 Test: tenant isolation for all monitor variants

## 9. Verificación Final

- [x] 9.1 Run full test suite: `pytest backend/tests/test_analisis_*.py -v` ensuring all pass
- [x] 9.2 Run lint/typecheck: verify no warnings in new files
- [x] 9.3 Verify all response models have `extra='forbid'`
- [x] 9.4 Verify `snake_case` is used throughout (no camelCase in Python)
- [x] 9.5 Verify file sizes: analisis_service.py ≤500 LOC, analisis router ≤200 LOC, each schema class is clean
- [x] 9.6 Verify no SQL queries in service (all DB access goes through existing repositories)
- [x] 9.7 Verify no business logic in router (all logic in AnalisisService)
- [x] 9.8 Run `openspec status --change "c-11-analisis-atrasados-reportes"` to confirm all artifacts complete
