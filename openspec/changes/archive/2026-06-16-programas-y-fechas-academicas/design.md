## Context

C-06 creó `Carrera`, `Cohorte`, `Materia` y el permiso `estructura:gestionar`. C-17 agrega dos entidades independientes pero relacionadas: programas de materia (documentos) y fechas académicas (calendario evaluativo). Ambas son parte del setup de cuatrimestre (FL-03).

**Restricciones**: modelos nuevos con BaseModelMixin. Routers separados `/api/programas` y `/api/fechas-academicas`. Reusa permiso existente `estructura:gestionar`. Sin dependencias nuevas.

## Goals / Non-Goals

**Goals:**
- `POST /api/programas` — upload programa (metadatos + referencia_archivo). Guard: `estructura:gestionar`.
- `GET /api/programas` — listar con filtros materia_id, carrera_id, cohorte_id.
- `GET /api/programas/{id}` — detalle.
- `PUT /api/programas/{id}` — reemplazar (nuevo título/archivo).
- `DELETE /api/programas/{id}` — soft delete.
- `POST /api/fechas-academicas` — crear fecha. Guard: `estructura:gestionar`.
- `GET /api/fechas-academicas` — tabla con filtros materia_id, cohorte_id, tipo.
- `GET /api/fechas-academicas/calendario` — vista agrupada por mes.
- `GET /api/fechas-academicas/cronograma-lms` — fragmento HTML para LMS.
- `PUT /api/fechas-academicas/{id}` — editar.
- `DELETE /api/fechas-academicas/{id}` — soft delete.

**Non-Goals:**
- Sin upload real de archivos (referencia_archivo es string — el storage es externo).
- Sin UI (→ C-23).
- Sin notificaciones de fechas.

## Decisions

### D1 — Routers separados

`/api/programas` y `/api/fechas-academicas` son dominios distintos (documentos vs calendario). Routers y servicios separados.

### D2 — Reusa `estructura:gestionar`

El permiso ya existe desde C-06. No se crean nuevos action codes ni seeds.

### D3 — `referencia_archivo` como string opaco

No se implementa upload binario. El campo guarda una referencia (URL, path, key) al archivo en storage externo. Esto mantiene el servicio simple y desacoplado del storage.

### D4 — Cronograma LMS: HTML simple

Similar a F6.4 de C-13. Tabla HTML con fechas agrupadas por tipo de evaluación. Sin dependencia de templates.

### D5 — Layout

```
backend/app/
├── api/v1/routers/{programas,fechas_academicas}.py
├── services/{programa_service,fecha_academica_service}.py
├── schemas/{programa,fecha_academica}.py
├── repositories/{programa_materia_repository,fecha_academica_repository}.py
├── models/{programa_materia,fecha_academica}.py
```

## Risks / Trade-offs

- **[Sin upload real]**: `referencia_archivo` es solo un string → Mitigación: el storage se maneja externamente (S3, sistema de archivos). Es suficiente para MVP.
