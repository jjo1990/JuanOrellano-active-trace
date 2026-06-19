## Why

C-06 construyó la estructura académica (Carrera, Cohorte, Materia), pero el sistema aún no tiene dónde centralizar los programas oficiales de cada materia ni las fechas clave de evaluaciones. El COORDINADOR necesita subir los PDFs de programas por materia × carrera × cohorte y registrar el cronograma de parciales, TPs y coloquios para que docentes y alumnos sepan cuándo es cada instancia. Sin `ProgramaMateria` y `FechaAcademica`, el setup de cuatrimestre (FL-03 pasos 5-6) queda incompleto.

## What Changes

- **F5.3 — Programas de materia**: endpoints `POST /api/programas` (subir PDF con título, materia, carrera, cohorte), `GET /api/programas` (listar con filtros), `GET /api/programas/{id}` (detalle), `PUT /api/programas/{id}` (reemplazar), `DELETE /api/programas/{id}` (soft delete). Guard: `estructura:gestionar` (ya existe de C-06).
- **F5.4 — Fechas académicas**: endpoints `POST /api/fechas-academicas` (registrar fecha de parcial/TP/coloquio), `GET /api/fechas-academicas` (tabla con filtros), `GET /api/fechas-academicas/calendario` (vista calendario), `PUT /api/fechas-academicas/{id}`, `DELETE /api/fechas-academicas/{id}`. Guard: `estructura:gestionar`.
- **Generación de contenido LMS**: endpoint `GET /api/fechas-academicas/cronograma-lms` que devuelve fragmento HTML con el cronograma de evaluaciones listo para publicar en el aula virtual.
- **Nuevos modelos**: `ProgramaMateria` (materia_id, carrera_id, cohorte_id, titulo, referencia_archivo) y `FechaAcademica` (materia_id, cohorte_id, tipo, numero, periodo, fecha, titulo).
- **Nueva migración Alembic**: tablas `programa_materia` y `fecha_academica`. Sin seed de permisos (reusa `estructura:gestionar`).

## Capabilities

### New Capabilities

- `programas-materia`: upload, listado, reemplazo y descarga de programas de materia en PDF. Filtrable por materia, carrera y cohorte.
- `fechas-academicas`: CRUD de fechas de evaluaciones con vistas tabular, calendario y generación de cronograma HTML para LMS.

### Modified Capabilities

Ninguna.

## Impact

- **Nuevo código**: `models/programa_materia.py`, `models/fecha_academica.py`, `schemas/programa.py`, `schemas/fecha_academica.py`, `api/v1/routers/programas.py`, `api/v1/routers/fechas_academicas.py`, `services/programa_service.py`, `services/fecha_academica_service.py`, repos correspondientes.
- **Modificado**: `models/__init__.py`, `main.py`.
- **Sin nuevos permisos**: reusa `estructura:gestionar` de C-06.
- **Migración**: tablas `programa_materia` y `fecha_academica` con FK a materia, carrera y cohorte.
- **Dependencia**: C-06 (`Materia`, `Carrera`, `Cohorte`).
- **Governance**: BAJO — catálogos y documentos, sin lógica de negocio compleja ni datos sensibles.
