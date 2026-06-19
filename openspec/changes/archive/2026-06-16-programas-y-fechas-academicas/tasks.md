## 1. Modelos SQLAlchemy

- [x] 1.1 Crear `models/programa_materia.py` con `ProgramaMateria(BaseModelMixin)`:
  - `__tablename__` = "programa_materia"
  - `materia_id`: UUID FK, NOT NULL
  - `carrera_id`: UUID FK, NOT NULL
  - `cohorte_id`: UUID FK, NOT NULL
  - `titulo`: str, NOT NULL
  - `referencia_archivo`: str, NOT NULL
  - `cargado_at`: datetime, default now
  - Indexes: tenant+materia, tenant+carrera+cohorte

- [x] 1.2 Crear `models/fecha_academica.py` con `FechaAcademica(BaseModelMixin)`:
  - `__tablename__` = "fecha_academica"
  - `materia_id`: UUID FK, NOT NULL
  - `cohorte_id`: UUID FK, NOT NULL
  - `tipo`: str (Parcial/TP/Coloquio/Recuperatorio), NOT NULL
  - `numero`: int, NOT NULL
  - `periodo`: str, NOT NULL
  - `fecha`: date, NOT NULL
  - `titulo`: str, NOT NULL
  - Indexes: tenant+materia+cohorte, tenant+fecha

- [x] 1.3 Actualizar `models/__init__.py` para exportar ambos

## 2. Migración Alembic

- [x] 2.1 Generar migración: CREATE TABLE programa_materia, fecha_academica con FK e índices
- [x] 2.2 Verificar upgrade/downgrade

## 3. Repositories

- [x] 3.1 (RED+GREEN) `repositories/programa_materia_repository.py`: CRUD + list_by_materia, list_by_carrera_cohorte
- [x] 3.2 (RED+GREEN) `repositories/fecha_academica_repository.py`: CRUD + list_with_filters, list_by_cohorte

## 4. Schemas Pydantic

- [x] 4.1 `schemas/programa.py`: ProgramaCreateRequest, ProgramaUpdateRequest, ProgramaResponse. `extra='forbid'`
- [x] 4.2 `schemas/fecha_academica.py`: FechaCreateRequest, FechaUpdateRequest, FechaResponse, CalendarioResponse, CronogramaResponse. `extra='forbid'`

## 5. Services

- [x] 5.1 (RED+GREEN) `services/programa_service.py`: CRUD simple. Tests.
- [x] 5.2 (RED+GREEN) `services/fecha_academica_service.py`: CRUD + calendario + HTML LMS. Tests.

## 6. Routers

- [x] 6.1 `api/v1/routers/programas.py`:
  - POST/GET /api/programas, GET/PUT/DELETE /api/programas/{id}. Guard: `estructura:gestionar`
- [x] 6.2 `api/v1/routers/fechas_academicas.py`:
  - POST/GET /api/fechas-academicas, GET /api/fechas-academicas/calendario, GET /api/fechas-academicas/cronograma-lms, PUT/DELETE /api/fechas-academicas/{id}. Guard: `estructura:gestionar`
- [x] 6.3 Registrar routers en `main.py`

## 7. Tests y verificación

- [x] 7.1 Tests repositorios (programa + fecha)
- [x] 7.2 Tests servicios
- [x] 7.3 `pytest` verde
- [x] 7.4 Cobertura ≥80%
- [x] 7.5 ≤500 LOC, `extra='forbid'`, sin hard delete, identidad JWT
