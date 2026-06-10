## Context

El backend ya tiene implementado auth JWT (C-03) con un campo `User.roles` como JSONB placeholder. Este design detalla cómo reemplazar ese placeholder con tablas RBAC reales, un servicio de resolución de permisos y un guard para endpoints.

**Estado actual:**
- `User.roles` es un JSONB `["PROFESOR", "COORDINADOR"]` — sin constraints, sin catálogo
- `core/permissions.py` es un placeholder vacío
- `core/dependencies.py` tiene `get_current_user` que devuelve `UserInfo` con `roles` desde el JWT
- Los roles se cargaban en el JWT (contra la recomendación de ARQUITECTURA.md §5.1)
- No existe ningún mecanismo de autorización por permiso

**Restricciones:**
- Multi-tenancy row-level: toda tabla de negocio lleva `tenant_id`
- Soft-delete siempre (heredado de `BaseModelMixin`)
- Los permisos se resuelven server-side, nunca viajan en el JWT
- Fail-closed: sin permiso explícito → 403
- NEXO no tiene permisos definidos en la matriz (PA-25, ADR-008 pendiente)

## Goals / Non-Goals

**Goals:**
- Modelos `Rol`, `Permiso`, `RolPermiso`, `UsuarioRol` con herencia de `BaseModelMixin`
- Migración 005 con seed de 7 roles y ~20 permisos con su matriz
- `PermissionService` que resuelve permisos efectivos por usuario+tenant
- `require_permission("modulo:accion")` dependency para endpoints FastAPI
- Catálogo administrable vía CRUD protegido con permisos
- El JWT ya NO lleva roles; se resuelven server-side

**Non-Goals:**
- No se implementa impersonación (es C-05 o posterior)
- No se implementa UI de administración de roles/permisos (frontend)
- No se implementa vigencia temporal de asignaciones con UI (solo modelo de datos preparado)
- No se definen permisos para NEXO (pendiente PA-25)

## Decisions

### D1: Tablas separadas (no JSONB)
- **Opción A (elegida)**: `rol`, `permiso`, `rol_permiso`, `usuario_rol` como tablas SQL con relaciones FK
- **Opción B**: Mantener JSONB en `user.roles` y agregar una tabla de catálogo de permisos
- **Por qué A**: Integridad referencial, queries eficientes, catálogo administrable, soft-delete por permiso individual. JSONB impide constraints FK y hace imposible la trazabilidad de cambios por permiso.

### D2: Roles en tabla general (no hardcode)
- **Opción A (elegida)**: Roles y permisos como datos seed en la base, administrables vía API
- **Opción B**: Roles hardcodeados como enum en código Python
- **Por qué A**: La KB exige un catálogo administrable por tenant (03_actores_y_roles.md §2: "Extensibilidad"). Roles hardcodeados impedirían que una institución tenga roles adicionales personalizados.

### D3: Permisos globales (`codigo` UNIQUE) vs por tenant
- **Opción A (elegida)**: `Permiso.codigo` es UNIQUE global (sin tenant_id). La matriz `rol_permiso` sí es scoped por tenant.
- **Opción B**: `Permiso` también con `tenant_id`
- **Por qué A**: Los permisos representan capacidades del sistema, no cambian por tenant. Lo que cambia es qué rol tiene cada permiso en cada tenant. Un permiso como `calificaciones:importar` significa lo mismo en toda institución.

### D4: `UsuarioRol` como tabla separada
- **Opción A (elegida)**: Tabla `usuario_rol` con `user_id`, `rol_id`, `fecha_desde`, `fecha_hasta` (vigencia)
- **Opción B**: Columna `rol_ids` array de UUIDs en `User`
- **Por qué A**: Permite vigencia temporal, histórico de asignaciones, y auditoría por asignación individual. Array de UUIDs no puede tener FK constraints.

### D5: Resolución de permisos en request (no cache)
- **Opción A (elegida)**: Se resuelven en cada request consultando la base (vía `PermissionService`)
- **Opción B**: Cache en Redis con TTL
- **Por qué A**: Simplicidad inicial. Los permisos raramente cambian intra-sesión; si hay necesidad de performance, se agrega cache después. Principio YAGNI.

### D6: `(propio)` manejado vía convention en el permiso, no vía permiso separado
- **Opción A (elegida)**: Los permisos con `(propio)` se resuelven con el mismo `codigo` pero requieren verificación adicional de contexto (el recurso pertenece al usuario). El guard `require_permission` soporta un callback opcional `context_check`.
- **Opción B**: Permisos separados `calificaciones:importar_propias` vs `calificaciones:importar_todas`
- **Por qué A**: Evita duplicar la matriz de permisos. El `(propio)` es un modificador de contexto, no un permiso diferente. Se implementa con un chequeo adicional en el endpoint.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| **R1**: Performance — resolución en cada request suma latencia | Queries simples (INNER JOINs indexados). Si es necesario, cache con TTL corto post-MVP |
| **R2**: Migración del JSONB a tablas relacionales puede perder datos | Script de migración que lee `user.roles` y crea las filas en `usuario_rol`. Rollback: restaurar backup + revertir migración |
| **R3**: NEXO sin permisos definidos (PA-25) | Seed con lista vacía de permisos. Documentado como decisión pendiente. Fácil de agregar después |
| **R4**: Catálogo administrable requiere endpoints CRUD protegidos | Los endpoints `rol` y `permiso` se protegen con `require_permission("usuarios:gestionar")`. Solo ADMIN por defecto |

## Migration Plan

### Forward (005_<hash>_rbac.py)
1. Crear tablas `rol`, `permiso`, `rol_permiso`, `usuario_rol`
2. Seed: insertar 7 roles (ALUMNO, TUTOR, PROFESOR, COORDINADOR, NEXO, ADMIN, FINANZAS)
3. Seed: insertar permisos (20+ códigos único global)
4. Seed: insertar filas en `rol_permiso` según matriz §3.3
5. Migrar datos: leer `user.roles` JSONB y crear filas en `usuario_rol` vinculando con el `rol.nombre` correcto
6. Opcional: dropear columna `user.roles` (o dejarla como deprecated)

### Rollback (downgrade)
1. Recrear columna `user.roles` como JSONB
2. Reconstruir desde `usuario_rol`
3. Dropear tablas `usuario_rol`, `rol_permiso`, `permiso`, `rol`

## Open Questions

- **OQ1**: ¿Dropear `user.roles` o mantenerlo como deprecated? Decisión: dropear — el JSONB ya no tiene sentido con tablas relacionales. La migración forward lleva los datos.
- **OQ2**: ¿Permisos de NEXO? Pendiente de PA-25 / ADR-008. Se seedea sin permisos.
