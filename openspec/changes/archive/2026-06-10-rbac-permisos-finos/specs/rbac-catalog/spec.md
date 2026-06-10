## ADDED Requirements

### Requirement: Modelos de datos RBAC
El sistema SHALL proveer los modelos SQLAlchemy `Rol`, `Permiso`, `RolPermiso` y `UsuarioRol` heredando de `BaseModelMixin` para soft-delete y tenant scope.

#### Scenario: Tabla rol tiene campos nombre y descripcion
- **WHEN** se inspecciona la tabla `rol`
- **THEN** contiene las columnas `id`, `tenant_id`, `nombre`, `descripcion`, `created_at`, `updated_at`, `deleted_at`
- **AND** `nombre` es UNIQUE dentro del tenant

#### Scenario: Tabla permiso tiene codigo unico global
- **WHEN** se inspecciona la tabla `permiso`
- **THEN** contiene las columnas `id`, `codigo`, `descripcion`, `modulo`, `created_at`, `updated_at`, `deleted_at`
- **AND** `codigo` es UNIQUE global (sin tenant_id)

#### Scenario: Tabla rol_permiso relaciona rol y permiso
- **WHEN** se inspecciona la tabla `rol_permiso`
- **THEN** contiene `rol_id` FK a `rol.id`, `permiso_id` FK a `permiso.id`, y `tenant_id`
- **AND** el par (`rol_id`, `permiso_id`, `tenant_id`) es UNIQUE

#### Scenario: Tabla usuario_rol asigna rol a usuario con vigencia
- **WHEN** se inspecciona la tabla `usuario_rol`
- **THEN** contiene `user_id` FK a `user.id`, `rol_id` FK a `rol.id`, `fecha_desde`, `fecha_hasta` (nullable)
- **AND** el par (`user_id`, `rol_id`) es UNIQUE dentro del tenant

### Requirement: Seed de roles del dominio
El sistema SHALL incluir en la migración 005 el seed de los 7 roles del dominio: ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS.

#### Scenario: Roles seed existen en tabla rol
- **WHEN** se ejecuta la migración 005
- **THEN** la tabla `rol` contiene los 7 roles con sus nombres canónicos

### Requirement: Seed de permisos de la matriz
El sistema SHALL incluir en la migración 005 el seed de todos los permisos definidos en la matriz §3.3 de `03_actores_y_roles.md`.

#### Scenario: Permisos seed existen en tabla permiso
- **WHEN** se ejecuta la migración 005
- **THEN** la tabla `permiso` contiene al menos los permisos: `calificaciones:importar`, `atrasados:ver`, `entregas:detectar_sin_corregir`, `comunicacion:enviar`, `comunicacion:aprobar`, `encuentros:gestionar`, `guardias:registrar`, `tareas:gestionar`, `avisos:publicar`, `equipos:asignar`, `estructura:gestionar`, `usuarios:gestionar`, `auditoria:ver`, `liquidaciones:grilla`, `liquidaciones:calcular`, `facturas:gestionar`, `tenant:configurar`, `estado:ver_propio`, `evaluaciones:reservar`, `avisos:confirmar`

### Requirement: Seed de matriz rol_permiso
El sistema SHALL incluir en la migración 005 el seed de todas las filas `rol_permiso` según la matriz de §3.3 de `03_actores_y_roles.md`.

#### Scenario: Rol_permiso contiene la matriz completa
- **WHEN** se ejecuta la migración 005
- **THEN** la tabla `rol_permiso` contiene las filas correspondientes a cada celda `✅` de la matriz
- **AND** NEXO no tiene permisos asignados (pendiente PA-25)

### Requirement: CRUD de roles (solo ADMIN)
El sistema SHALL proveer endpoints para listar, crear, actualizar y soft-deletear roles, accesibles solo con permiso `usuarios:gestionar`.

#### Scenario: ADMIN lista roles
- **WHEN** un usuario con permiso `usuarios:gestionar` hace GET a `/api/v1/roles`
- **THEN** recibe un listado paginado de roles del tenant

#### Scenario: ADMIN crea rol custom
- **WHEN** un usuario con permiso `usuarios:gestionar` hace POST a `/api/v1/roles` con `{nombre, descripcion}`
- **THEN** se crea un nuevo rol scoped al tenant
- **AND** el nombre debe ser UNIQUE dentro del tenant

#### Scenario: Usuario sin permiso recibe 403
- **WHEN** un usuario SIN permiso `usuarios:gestionar` accede a cualquier endpoint CRUD de roles
- **THEN** recibe HTTP 403

### Requirement: CRUD de permisos (solo ADMIN)
El sistema SHALL proveer endpoints para listar permisos (solo lectura pública autenticada) y administrar (solo ADMIN).

#### Scenario: Usuario autenticado lista permisos
- **WHEN** cualquier usuario autenticado hace GET a `/api/v1/permisos`
- **THEN** recibe el listado completo de permisos del sistema (globales)

#### Scenario: ADMIN administra matriz rol_permiso
- **WHEN** un usuario con permiso `usuarios:gestionar` asigna/quita un permiso a un rol
- **THEN** la fila en `rol_permiso` se crea/soft-deletea
