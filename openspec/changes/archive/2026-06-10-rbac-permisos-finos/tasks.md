## 1. Modelos RBAC

- [x] 1.1 Crear test de modelos `Rol`, `Permiso`, `RolPermiso`, `UsuarioRol` (herencia BaseModelMixin, constraints, FKs)
- [x] 1.2 Implementar modelo `Rol` en `app/models/rol.py` (nombre unique por tenant, descripcion)
- [x] 1.3 Implementar modelo `Permiso` en `app/models/permiso.py` (codigo unique global, descripcion, modulo)
- [x] 1.4 Implementar modelo `RolPermiso` en `app/models/rol_permiso.py` (FK rol, FK permiso, unique compuesto)
- [x] 1.5 Implementar modelo `UsuarioRol` en `app/models/usuario_rol.py` (FK user, FK rol, fecha_desde, fecha_hasta)
- [x] 1.6 Registrar todos los modelos en `app/models/__init__.py`

## 2. PermissionService

- [x] 2.1 Crear tests de `PermissionService` (unión de roles, vigencia, tenant isolation, fail-closed)
- [x] 2.2 Implementar `PermissionService` en `app/core/permissions.py` con método `get_effective_permissions(user_id, tenant_id) -> set[str]`
- [x] 2.3 No crear repositorio separado — inline queries (YAGNI, según design.md). El servicio es suficientemente simple.

## 3. require_permission dependency

- [x] 3.1 Crear tests de `require_permission` (con permiso → pasa, sin permiso → 403, context_check, token inválido → 401)
- [x] 3.2 Implementar `require_permission(permiso: str, context_check: Optional[Callable] = None)` en `app/core/dependencies.py`
- [x] 3.3 Slim down del JWT: quitar `roles` del payload en `app/core/security.py` y resolver desde DB en `get_current_user`

## 4. Migración 005 y seed data

- [x] 4.1 Generar migración Alembic 005 con creación de tablas `rol`, `permiso`, `rol_permiso`, `usuario_rol`
- [x] 4.2 Agregar seed de roles (7 roles del dominio)
- [x] 4.3 Agregar seed de permisos (~20 códigos de la matriz §3.3)
- [x] 4.4 Agregar seed de `rol_permiso` según matriz de §3.3 (NEXO sin permisos)
- [x] 4.5 Agregar migración de datos: leer `user.roles` JSONB → insertar en `usuario_rol`
- [x] 4.6 Dropear columna `user.roles` (JSONB)
- [x] 4.7 Ejecutar migración y verificar en DB que seed data existe

## 5. CRUD de catálogo administrable

- [x] 5.1 Crear tests de endpoints CRUD de roles (listar, crear, soft-delete; ADMIN OK, sin permiso → 403)
- [x] 5.2 Implementar router `app/api/v1/routers/roles.py` con CRUD de roles protegido con `require_permission("usuarios:gestionar")`
- [x] 5.3 Crear tests de endpoints de permisos (listar público autenticado, asignar/quitar solo ADMIN)
- [x] 5.4 Implementar router `app/api/v1/routers/permisos.py` con listado global de permisos; asignar/quitar va en `roles.py`
- [x] 5.5 Registrar routers en `app/main.py`

## 6. Tests de integración

- [x] 6.1 Test: usuario sin permiso → 403 en endpoint protegido
- [x] 6.2 Test: unión de roles (usuario con PROFESOR+COORDINADOR tiene permisos de ambos)
- [x] 6.3 Test: permiso `(propio)` con context_check funciona correctamente (propio → OK, ajeno → 403)
- [x] 6.4 Test: catálogo administrable — ADMIN puede listar/crear roles, usuario sin permiso no puede
- [x] 6.5 Test: aislamiento de tenant — usuario del tenant A no ve roles del tenant B
