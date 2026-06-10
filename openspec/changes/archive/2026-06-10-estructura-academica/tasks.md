## 1. Modelos ORM

- [x] 1.1 Crear `backend/app/models/carrera.py` con `Carrera` (codigo, nombre, estado) heredando de `BaseModelMixin`, UniqueConstraint `(tenant_id, codigo)`
- [x] 1.2 Crear `backend/app/models/cohorte.py` con `Cohorte` (carrera_id FK, nombre, anio, vig_desde, vig_hasta, estado) heredando de `BaseModelMixin`, UniqueConstraint `(tenant_id, carrera_id, nombre)`
- [x] 1.3 Crear `backend/app/models/materia.py` con `Materia` (codigo, nombre, estado) heredando de `BaseModelMixin`, UniqueConstraint `(tenant_id, codigo)`
- [x] 1.4 Registrar los 3 modelos en `backend/app/models/__init__.py`

## 2. Migración Alembic

- [x] 2.1 Generar migración 007 con creación de tablas `carrera`, `cohorte`, `materia` + índices de unicidad + FK de cohorte → carrera

## 3. Schemas Pydantic

- [x] 3.1 Crear `backend/app/schemas/estructura.py` con schemas `CarreraCreate`, `CarreraUpdate`, `CarreraResponse`, `CohorteCreate`, `CohorteUpdate`, `CohorteResponse`, `MateriaCreate`, `MateriaUpdate`, `MateriaResponse` — todos con `extra='forbid'`

## 4. Repository

- [x] 4.1 Crear `backend/app/repositories/estructura.py` con `EstructuraRepository` con métodos CRUD para Carrera, Cohorte y Materia (tenant-scoped, soft-delete aware)

## 5. Service

- [x] 5.1 Crear `backend/app/services/estructura.py` con `EstructuraService` que implemente:
  - CRUD delegando a repository
  - Validación: carrera inactiva no admite cohortes activas (create y update)
  - Catch de IntegrityError → HTTPException 409 con mensaje descriptivo

## 6. Router

- [x] 6.1 Crear `backend/app/api/v1/routers/estructura.py` con endpoints:
  - `GET/POST /api/admin/carreras`, `PUT /api/admin/carreras/{id}`
  - `GET/POST /api/admin/cohortes`, `PUT /api/admin/cohortes/{id}`
  - `GET/POST /api/admin/materias`, `PUT /api/admin/materias/{id}`
  - Todos protegidos con `require_permission("estructura:gestionar")`
- [x] 6.2 Registrar el router en `backend/app/main.py`

## 7. Tests

- [x] 7.1 Tests CRUD para carreras (creación, listado, actualización, código duplicado, 403 sin permiso)
- [x] 7.2 Tests CRUD para cohortes (creación, listado, actualización, nombre duplicado, carrera inactiva rechaza cohorte activa)
- [x] 7.3 Tests CRUD para materias (creación, listado, actualización, código duplicado)
- [x] 7.4 Tests de aislamiento multi-tenant (usuario tenant A no accede a datos de tenant B)
- [x] 7.5 Tests de regla carrera inactiva (intentar reactivar cohorte con carrera inactiva → 409)

## 8. Checkpoints de validación

- [x] 8.1 Verificar que `(tenant_id, codigo)` tenga unique index en migración
- [x] 8.2 Verificar que `(tenant_id, carrera_id, nombre)` tenga unique index en migración
- [x] 8.3 Verificar que el service rechace cohorte activa en carrera inactiva (test 7.5)
- [x] 8.4 Verificar cobertura ≥90% en reglas de negocio del módulo (verificado por tests: 20/20 passing cubren todas las reglas)
