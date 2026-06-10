## Why

Activia-trace necesita modelar la estructura académica base — Carreras, Cohortes y Materias — como entidades raíz del dominio. Sin estos modelos ningún módulo downstream (asignaciones, equipos docentes, padrones, calificaciones, comunicaciones) puede operar. Es el primer paso después de tener auth y RBAC listos (C-04).

## What Changes

- Modelos SQLAlchemy: `Carrera`, `Cohorte`, `Materia` heredando de `BaseModelMixin` (soft-delete, tenant_id, timestamps)
- ABM protegido con `require_permission("estructura:gestionar")` — solo ADMIN
- Rutas: `POST/GET/PUT /api/admin/carreras`, `POST/GET/PUT /api/admin/cohortes`, `POST/GET/PUT /api/admin/materias`
- Reglas: unicidad `(tenant_id, codigo)` en Carrera/Materia; `(tenant_id, carrera_id, nombre)` en Cohorte; carrera inactiva no admite cohortes abiertas
- Migración Alembic 007 con las tres tablas
- Tests de CRUD, unicidad multi-tenant, aislamiento y estado activa/inactiva

## Capabilities

### New Capabilities

- `admin-carreras`: ABM de carreras con código único por tenant, nombre y estado activa/inactiva
- `admin-cohortes`: ABM de cohortes vinculadas a una carrera, con nombre único por `(tenant, carrera)`, año, vigencia y estado
- `admin-materias`: ABM de materias con código único por tenant, nombre y estado activa/inactiva

### Modified Capabilities

Ninguna — C-06 es el primer módulo de dominio sobre la plataforma RBAC existente.

## Impact

- `backend/app/models/carrera.py`, `cohorte.py`, `materia.py` — 3 nuevos modelos ORM
- `backend/app/schemas/estructura.py` — schemas Pydantic con `extra='forbid'`
- `backend/app/repositories/estructura.py` — repos con tenant scope por defecto
- `backend/app/services/estructura.py` — service con regla de carrera inactiva → no cohortes activas
- `backend/app/api/v1/routers/estructura.py` — 3 grupos de endpoints protegidos
- `backend/alembic/versions/007_estructura_academica.py` — nueva migración
- `backend/app/models/__init__.py` — registro de los 3 nuevos modelos
- `backend/tests/` — test suite del módulo
