## 1. EncryptedField descriptor y limpieza del modelo User

- [x] 1.1 Crear `backend/app/models/fields.py` con descriptor `EncryptedField` que cifra al setear y descifra al leer usando `core/security.encrypt/decrypt`
- [x] 1.2 Reescribir `backend/app/models/user.py`: agregar `nombre`, `apellidos`, `dni` (EncryptedField), `cuil` (EncryptedField), `cbu` (EncryptedField), `alias_cbu` (EncryptedField), `banco`, `regional`, `legajo`, `legajo_profesional`, `facturador`, `activo`
- [x] 1.3 Eliminar `display_name` y `roles` del modelo User (roles ya dropeado en DB)
- [x] 1.4 Mantener `UniqueConstraint(tenant_id, email)` y `Index(ix_user_email_tenant)`

## 2. Modelo Asignacion

- [x] 2.1 Crear `backend/app/models/asignacion.py` con SQLAlchemy model: `usuario_id`, `rol_id`, `materia_id`, `carrera_id`, `cohorte_id` (FKs nullable), `comisiones` (JSONB), `responsable_id` (self-FK nullable a User), `desde` (Date), `hasta` (Date nullable)
- [x] 2.2 Heredar de `BaseModelMixin` + `Base` (tenant_id, soft delete)
- [x] 2.3 Agregar índices: `(tenant_id, usuario_id)`, `(tenant_id, rol_id)`, `(tenant_id, materia_id)`

## 3. Schemas Pydantic

- [x] 3.1 Crear `backend/app/schemas/usuario.py`: `UsuarioCreate`, `UsuarioUpdate`, `UsuarioResponse` (sin PII expuesta), `UsuarioStatusUpdate` — todos con `extra='forbid'`
- [x] 3.2 Actualizar `backend/app/schemas/auth.py` `UserInfo`: agregar `nombre`, `apellidos`, derivar `display_name` como property; quitar `roles` del schema (se resuelve server-side)
- [x] 3.3 Crear `backend/app/schemas/asignacion.py`: `AsignacionCreate`, `AsignacionUpdate`, `AsignacionResponse`, `AsignacionListParams` — todos con `extra='forbid'`

## 4. Repositorios

- [x] 4.1 Extender `backend/app/repositories/user_repository.py` con métodos: `get_by_email`, `list_by_tenant`, `search_by_name`, `filter_by_active`
- [x] 4.2 Crear `backend/app/repositories/asignacion_repository.py` con CRUD + métodos: `list_by_usuario`, `list_vigentes`, `list_by_materia`, `list_by_rol`, `filter_by_context`

## 5. Services

- [x] 5.1 Crear `backend/app/services/usuario_service.py`: create con cifrado automático de PII, update con merge de campos, list con filtros, desactivación
- [x] 5.2 Crear `backend/app/services/asignacion_service.py`: create (valida FKs existentes, valida fechas), update (no permite cambiar usuario_id ni tenant_id), delete (soft), `is_vigente()` helper, list con filtros de contexto y vigencia

## 6. Routers y dependencies

- [x] 6.1 Crear `backend/app/api/v1/routers/usuarios.py`: `GET/POST /api/admin/usuarios`, `GET/PUT /api/admin/usuarios/{id}`, `PATCH /api/admin/usuarios/{id}/status` — todos con `require_permission("usuarios:gestionar")`
- [x] 6.2 Crear `backend/app/api/v1/routers/asignaciones.py`: `GET/POST /api/asignaciones`, `GET/PUT/DELETE /api/asignaciones/{id}` — todos con `require_permission("equipos:asignar")`
- [x] 6.3 Registrar ambos routers en `backend/app/main.py`

## 7. Migración 008

- [x] 7.1 Crear `backend/alembic/versions/008_usuarios_asignaciones.py`: alter table user (add columns, drop display_name, drop roles si existe), create table asignacion (all columns + FKs + indexes)
- [x] 7.2 Verificar que `email` existente en user se preserva sin cambios
- [x] 7.3 Registrar en el script: `down_revision = "007"` (última migración de C-06)

## 8. Integración con auth y RBAC existente

- [x] 8.1 Actualizar `get_current_user` en `core/dependencies.py` para que `UserInfo` use `nombre` + `apellidos` en lugar de `display_name`
- [x] 8.2 Verificar que el login fluye correctamente: `user.email` se mantiene sin cifrar (solo PII se cifra), `get_by_email` funciona
- [x] 8.3 Verificar que `require_permission` funciona contra asignaciones vigentes (no solo contra `usuario_rol` de C-04)

## 9. Tests

- [x] 9.1 Test: PII cifrada en DB (verificar que `dni`, `cuil`, `cbu`, `alias_cbu` se almacenan cifrados y se descifran al leer)
- [x] 9.2 Test: Response de usuario NO expone PII (dni, cuil, cbu, alias_cbu no aparecen en responses)
- [x] 9.3 Test: Unicidad `(tenant_id, email)` — crear dos usuarios con mismo email en mismo tenant → 409
- [x] 9.4 Test: Unicidad cross-tenant — mismo email en tenants distintos OK
- [x] 9.5 Test: CRUD asignaciones — crear, listar, obtener, actualizar, soft delete
- [x] 9.6 Test: Vigencia — asignación vencida no autoriza permisos; vigente sí
- [x] 9.7 Test: Multi-rol — usuario con dos asignaciones vigentes (ej: PROFESOR y COORDINADOR) tiene unión de permisos
- [x] 9.8 Test: Jerarquía — asignación con `responsable_id` referenciando a otro usuario
- [x] 9.9 Test: Filtros de asignaciones por materia, vigencia, usuario, rol
- [x] 9.10 Test: Aislamiento multi-tenant — usuario del tenant A no ve/crea/modifica datos del tenant B
- [x] 9.11 Test: Soft delete en asignacion — DELETE marca `deleted_at`, GET no lo retorna
- [x] 9.12 Test: Estado activo/inactivo de usuario — inactivo no puede hacer login
- [x] 9.13 Test: Migración 008 metadata y revisión
