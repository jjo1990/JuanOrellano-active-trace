## Why

C-03 (`auth-jwt-2fa`) dejó el campo `roles` en el modelo `User` como un placeholder JSONB (`["PROFESOR", "COORDINADOR"]`). Para cumplir con la regla de negocio de **RBAC con permisos finos** —donde cada endpoint exige un permiso explícito `modulo:accion` y la matriz rol×permiso es un catálogo administrable— necesitamos reemplazar ese placeholder con tablas reales, un servicio de resolución de permisos server-side y un guard de autorización para los endpoints.

## What Changes

- **Nuevas tablas**: `rol`, `permiso`, `rol_permiso` con herencia de `BaseModelMixin` (soft-delete, tenant scope).
- **Migración 005**: Creación de tablas + seed de la matriz base de roles y permisos.
- **Migración del modelo `User`**: El campo `roles` JSONB se reemplaza por una relación M:N hacia `Rol`. Se agrega `UsuarioRol` como tabla intermedia con vigencia temporal.
- **`PermissionService`**: Resuelve permisos efectivos de un usuario (unión de roles, acotada por tenant y vigencia).
- **`require_permission("modulo:accion")`**: FastAPI dependency que verifica el permiso del usuario autenticado; sin permiso → `403`.
- **Seed data**: Roles del dominio (ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS) y matriz completa de §3.3 de `03_actores_y_roles.md`.
- **Catálogo administrable**: Endpoints CRUD para roles y permisos (solo ADMIN).
- **Tests**: sin permiso → 403, unión de roles, permiso `(propio)` vs global, catálogo administrable.

## Capabilities

### New Capabilities
- `rbac-catalog`: Catálogo administrable de roles, permisos y asignación rol×permiso (datos, seed, migración)
- `permission-resolution`: Servicio de resolución de permisos efectivos por usuario+tenant con vigencia temporal
- `require-permission-guard`: Dependency guard `require_permission("modulo:accion")` para endpoints FastAPI

### Modified Capabilities
- N/A — primer cambio que introduce el modelo RBAC real

## Impact

- **Modelos**: `User.roles` JSONB → relación M:N con `Rol` vía `UsuarioRol` (migración de datos incluida)
- **Core**: Nuevo `core/permissions.py` con `PermissionService` + `core/dependencies.py` se extiende con `require_permission`
- **Auth**: El JWT ya no necesita cargar roles; se resuelven server-side (alineado con ARQUITECTURA.md §5.1)
- **Migraciones**: Una nueva migración Alembic (005) + seed data
- **NEXO**: Se seedea sin permisos (PA-25 pendiente de definición de negocio — ver ADR-008)
