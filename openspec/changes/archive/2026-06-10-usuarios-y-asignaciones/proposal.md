## Why

El modelo `User` actual es un placeholder con solo campos de auth (`email`, `password_hash`, `display_name`, `roles` JSONB). No soporta los datos reales del dominio docente: PII (DNI, CUIL, CBU), datos bancarios, regional, legajo, ni el modelo de asignaciones que vincula usuarios con roles y contexto académico (materia/carrera/cohorte). Sin este cambio, ningún módulo posterior (equipos docentes, liquidaciones, comunicaciones) puede operar.

Además, la columna `roles` JSONB de `User` ya fue dropeada en DB por la migración 005 (C-04), pero el modelo Python aún la referencia. C-07 limpia esa deuda técnica.

## What Changes

- **Modelo `User` completo**: agrega campos PII (dni, cuil, cbu, alias_cbu) cifrados con AES-256-GCM, nombre+apellidos (reemplazan `display_name`), datos del docente (regional, legajo, legajo_profesional, facturador, banco) y estado activo/inactivo.
- **BREAKING**: Se elimina el campo `display_name` del modelo y schemas — se deriva de `nombre + apellidos`.
- **BREAKING**: Se elimina la columna `roles` del modelo Python (ya dropeada en DB por C-04).
- **Modelo `Asignacion`**: vincula `User` ↔ `Rol` ↔ contexto académico (`Materia`/`Carrera`/`Cohorte`) con `comisiones` (JSONB), `responsable_id` (jerarquía), vigencia `desde`/`hasta`. Reemplaza a `usuario_rol` (C-04) como el mecanismo principal de asignación de roles con contexto.
- **ABM usuarios** en `/api/admin/usuarios` protegido con `require_permission("usuarios:gestionar")` (ADMIN).
- **CRUD asignaciones** en `/api/asignaciones` protegido con `require_permission("equipos:asignar")` (COORDINADOR, ADMIN).
- **Migración 008**: modifica `user` table (agrega columnas, dropea `display_name` y obsoletas) + crea `asignacion` table.
- **Deprecación de `usuario_rol`**: la tabla de C-04 se conserva para datos existentes pero deja de ser el mecanismo activo de asignación. Asignacion es el reemplazo con contexto académico completo.

## Capabilities

### New Capabilities
- `admin-users`: ABM de usuarios del tenant con gestión de PII, datos bancarios y estado (ADMIN).
- `asignaciones`: CRUD de asignaciones usuario ↔ rol ↔ contexto académico con vigencia, jerarquía y comisiones (COORDINADOR, ADMIN).

### Modified Capabilities
- *(ninguna — no hay specs previas en este proyecto)*

## Impact

- **Modelos**: `backend/app/models/user.py` reescrito con PII cifrada. Nuevo `backend/app/models/asignacion.py`.
- **Schemas**: `backend/app/schemas/auth.py` (`UserInfo`) modificado para usar `nombre+apellidos` en lugar de `display_name`. Nuevos schemas de usuario y asignación.
- **Services**: Nuevo `backend/app/services/usuario_service.py` (lógica de cifrado/descifrado de PII). Nuevo `backend/app/services/asignacion_service.py` (vigencia, jerarquía).
- **Repositories**: Nuevo `backend/app/repositories/usuario_repository.py` (extiende el actual `UserRepository`). Nuevo `backend/app/repositories/asignacion_repository.py`.
- **Routers**: Nuevos `backend/app/api/v1/routers/usuarios.py` y `backend/app/api/v1/routers/asignaciones.py`.
- **Migración**: `backend/alembic/versions/008_usuarios_asignaciones.py`.
- **Dependencias**: `cryptography` ya disponible (usado en `core/security.py` para AES-256-GCM).
