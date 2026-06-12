## Why

C-10 entregó los modelos `Calificacion` y `UmbralMateria` con toda la ingesta de datos lista. Ahora el docente necesita **ver y entender** el estado académico de sus alumnos: quiénes están atrasados, cómo se rankean por actividades aprobadas, qué TPs quedan sin corregir y cómo va la materia en general. Sin esta capa de análisis, los datos importados no generan valor — son solo registros crudos en la base. Este change cierra el flujo central del PROFESOR: importar → analizar (ya con datos reales para comunicar en C-12).

## What Changes

- Nuevo `AnalisisService` con pura computación sobre `Calificacion` y `UmbralMateria` (sin persistencia nueva, sin migración).
- Schemas de respuesta (`analisis.py`) con DTOs tipados para cada endpoint de análisis.
- Router `/api/analisis/*` con 8 endpoints protegidos por el permiso `atrasados:ver`.
- Cómputo de alumnos atrasados según RN-06 (actividades faltantes o nota < umbral).
- Ranking de actividades aprobadas según RN-09 (≥1 aprobada, orden descendente).
- Reportes rápidos por materia con métricas clave.
- Notas finales agrupadas por alumno.
- Detección de TPs sin corregir según RN-07/RN-08 (solo escala textual).
- Monitor general con filtros (materia, regional, comision, alumno, estado) para COORD/ADMIN.
- Monitor de seguimiento para TUTOR/PROFESOR y monitor admin con rango de fechas.
- Nuevo action code `ANALISIS_CONSULTAR` para auditoría.
- Permiso `atrasados:ver` registrado en seed de permisos.
- Tests unitarios y de integración para cada algoritmo de cómputo, tenant isolation incluida.

## Capabilities

### New Capabilities

- `atrasados-detection`: cómputo de alumnos atrasados por materia aplicando RN-06 (actividades faltantes o nota < umbral configurado).
- `ranking-aprobadas`: ranking de alumnos por cantidad de actividades aprobadas, filtrando ≥1 aprobada (RN-09).
- `reportes-rapidos`: vista consolidada de métricas clave por materia (total alumnos, aprobación, distribución de notas) con estado informativo cuando no hay datos.
- `notas-finales`: agrupación de calificaciones por alumno con nota final calculada.
- `tps-sin-corregir`: cruce de reporte de finalización vs calificaciones para detectar entregas de escala textual sin nota (RN-07, RN-08).
- `monitor-general`: vista transversal con filtros query params (materia, regional, comision, alumno, estado) para COORD/ADMIN.
- `monitor-seguimiento`: vista de seguimiento por docente (TUTOR/PROFESOR) con filtros por alumno, comision, regional, actividad.
- `monitor-admin`: vista de coordinación/admin extendiendo monitor-seguimiento con filtro adicional de rango de fechas.

### Modified Capabilities

Ninguna. Este change no modifica specs existentes — agrega funcionalidad nueva sobre modelos de C-10.

## Impact

- `backend/app/services/analisis_service.py` (nuevo) — servicio de cómputo puro.
- `backend/app/schemas/analisis.py` (nuevo) — DTOs de respuesta con `extra='forbid'`.
- `backend/app/api/v1/routers/analisis.py` (nuevo) — 8 endpoints GET con guard `atrasados:ver`.
- `backend/app/core/action_codes.py` — nuevo código `ANALISIS_CONSULTAR`.
- `backend/app/core/permissions.py` — seed de permiso `atrasados:ver`.
- `backend/tests/` — 4 archivos nuevos de tests (atrasados, ranking, reportes, monitor).
- Sin migración (no se crean tablas ni columnas nuevas).
- Sin cambios en modelos existentes, repositorios, ni routers previos.
