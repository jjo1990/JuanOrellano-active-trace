## Context

El backend tiene el modelo `User` como placeholder (C-03) con solo campos de auth y `roles` JSONB. La columna `roles` ya fue dropeada en DB (migración 005 de C-04), pero el modelo Python aún la declara. C-04 también creó `usuario_rol` como vínculo simple user↔rol sin contexto académico. C-06 agregó `Carrera`, `Cohorte`, `Materia`.

**Estado actual de modelos disponibles:**
- `User`: id, tenant_id, email, password_hash, totp_secret, totp_enabled, display_name, roles (en Python pero no en DB)
- `Rol`: id, tenant_id, nombre, descripcion
- `Permiso`: id, codigo, descripcion, modulo
- `RolPermiso`, `UsuarioRol`
- `Carrera`, `Cohorte`, `Materia`
- `AuditLog`

**Estado actual de migraciones:** 001 (tenant) → 002 (user) → 003 (refresh_token) → 004 (password_reset_token) → 005 (RBAC) → 006 (audit_log) → 007 (estructura_academica). La 008 es la siguiente.

**Restricciones:**
- Multi-tenancy row-level: toda tabla lleva `tenant_id`
- Soft-delete siempre (heredado de `BaseModelMixin`)
- PII cifrada con AES-256-GCM (funciones `encrypt`/`decrypt` ya en `core/security.py`)
- ≤500 LOC por archivo backend
- snake_case en todo Python, schemas Pydantic con `extra='forbid'`
- Identidad desde sesión JWT, nunca desde parámetros de request

## Goals / Non-Goals

**Goals:**
- Modelo `User` completo con PII cifrada (dni, cuil, cbu, alias_cbu → AES-256-GCM; nombre, apellidos, banco, regional, legajo, legajo_profesional, facturador, activo → texto plano)
- Eliminar `display_name` del modelo y schemas (derivar de nombre+apellidos)
- Eliminar `roles` del modelo Python (ya dropeado en DB)
- Modelo `Asignacion` con FK a `User`, `Rol`, `Materia`/`Carrera`/`Cohorte` (nullable según contexto), comisiones JSONB, responsable_id (self-FK a User), vigencia desde/hasta
- Servicio de cifrado/descifrado automático para campos PII en el repositorio/schema
- ABM usuarios en `/api/admin/usuarios` con `require_permission("usuarios:gestionar")`
- CRUD asignaciones en `/api/asignaciones` con `require_permission("equipos:asignar")`
- Unicidad `(tenant_id, email)` en User
- Regla: asignación vencida no otorga permisos (se conserva como histórico)
- Migración 008: alter user table + create asignacion table
- Tests: PII no expuesta, unicidad email, vigencia, multi-rol, jerarquía

**Non-Goals:**
- No se implementa el modelo `Dictado` (ADR-006) — pendiente
- No se implementa lógica de clonado de equipo entre períodos (C-08)
- No se implementa asignación masiva de docentes (C-08)
- No se implementa UI frontend para ABM usuarios/asignaciones
- No se implementa migración de datos de `usuario_rol` a `asignacion` (tabla se conserva como histórica)

## Decisions

### D1: Cifrado automático de PII vía descriptor/hybrid property
- **Opción A (elegida)**: Usar un descriptor Python (`EncryptedField`) que cifra al setear y descifra al leer, aplicado en el modelo SQLAlchemy
- **Opción B**: Cifrar/descifrar en el service layer antes de pasar al repository
- **Opción C**: Cifrar/descifrar a nivel de schema Pydantic
- **Por qué A**: El cifrado está atado al modelo, no al service ni al schema. Esto garantiza que cualquier camino de escritura (service, script, seed) cifre automáticamente. Opción B requiere que CADA service lo haga explícitamente — alto riesgo de fuga de PII. Opción C no protege si alguien accede al modelo directamente. El descriptor maneja serialización/deserialización transparente: en DB se guarda el string cifrado, en Python se lee como texto plano.

### D2: `display_name` → derivado de `nombre + apellidos`
- **Opción A (elegida)**: Eliminar `display_name` del modelo y schema. En `UserInfo` se devuelve `display_name` como property derivada `f"{nombre} {apellidos}"`.
- **Opción B**: Mantener `display_name` como campo opcional, si se proporciona usarlo, si no derivar
- **Por qué A**: Simplifica el modelo. La KB define `nombre` + `apellidos` como campos base. Un display_name separado introduce dualidad de fuente de verdad. Los schemas de response pueden exponer `nombre`, `apellidos` y una property `display_name` derivada en el schema para no romper clientes existentes.

### D3: `Asignacion.rol_id` como FK a `Rol` (catálogo administrable)
- **Opción A (elegida)**: FK a `rol.id` en lugar de enum hardcodeado
- **Opción B**: Enum en Python `RolEnum`
- **Por qué A**: La KB §E5 define `rol: enum` conceptualmente, pero §2 de 03_actores_y_roles.md exige un catálogo administrable por tenant. Usar FK a `Rol` (C-04) mantiene consistencia con el sistema RBAC existente. Un enum hardcodeado impediría agregar roles sin modificar código.

### D4: `Asignacion` reemplaza funcionalmente a `usuario_rol`
- **Opción A (elegida)**: `Asignacion` es el nuevo mecanismo de asignación con contexto académico. `usuario_rol` se conserva para datos históricos pero no se usa en nuevas funcionalidades.
- **Opción B**: Migrar datos de `usuario_rol` a `asignacion` y dropear `usuario_rol`
- **Por qué A**: Migrar datos existentes de `usuario_rol` (que no tienen materia/carrera/cohorte) requeriría datos default o nulos — riesgo de pérdida. Conservar la tabla como histórica es seguro. Los nuevos endpoints de asignación operan sobre `Asignacion`. En C-08 (equipos-docentes) se define si se hace una migración one-time.

### D5: Asignacion `hasta` nullable = abierta
- **Opción A (elegida)**: `hasta` nullable; `null` = sin fecha de cierre (abierta)
- **Opción B**: Campo booleano `abierta` separado + `hasta` nullable
- **Por qué A**: Consistente con todas las entidades del modelo (04_modelo_de_datos.md §Convenciones: `vig_hasta` nulo = abierto). Evita dualidad de datos.

### D6: `responsable_id` como self-FK nullable a User
- **Opción A (elegida)**: FK a `user.id` sobre la misma tabla
- **Opción B**: FK a `asignacion.id` (jerarquía entre asignaciones)
- **Por qué A**: El responsable es una PERSONA (quién supervisa), no otra asignación. La KB §E5 dice "FK → Usuario (quién supervisa: coordinador responsable)". La jerarquía entre asignaciones se resuelve consultando qué asignación del responsable aplica al mismo contexto.

### D7: `comisiones` como JSONB no normalizado
- **Opción A (elegida)**: `comisiones: list[str]` como JSONB en Asignacion
- **Opción B**: Tabla separada `asignacion_comision`
- **Por qué A**: Las comisiones son etiquetas (strings) sin atributos propios. JSONB evita join adicional y simplifica el modelo. Si en el futuro las comisiones tienen metadatos (cupo, horario), se normalizan.

### D8: Unicidad `(tenant_id, email)` cross-estado (incluye inactivos)
- **Opción A (elegida)**: UniqueConstraint sobre `(tenant_id, email)` sin filtrar por `deleted_at`
- **Opción B**: Partial unique index que excluye `deleted_at IS NOT NULL`
- **Por qué A**: El email debe ser único en todo el tenant, incluso entre usuarios inactivos o soft-deleted, para evitar colisiones al reactivar. Si se necesita reusar un email, se debe hacer un cambio explícito. Esto es consistente con la KB: "El par `(tenant_id, email)` es único".

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| **R1**: Cifrado automático vía descriptor puede afectar queries de búsqueda por email (no se puede buscar contra texto cifrado) | El email cifrado no es buscable directamente. Para login, se descifran todos los emails del tenant o se mantiene un hash HMAC del email para lookup. **Decisión**: mantener la búsqueda por email en el repositorio sin cambios por ahora — login usa `get_by_email` que compara el string plano (la columna almacena texto cifrado). Esto funciona si el lookup se hace sobre la sesión del tenant (scope reducido). Si hay problemas de performance, agregar columna `email_hash` para lookup. Ver D9 en open questions. |
| **R2**: El descriptor `EncryptedField` puede no ser compatible con queries SQLAlchemy que referencian la columna directamente | Usar `mapped_column` estándar (almacena texto cifrado). El descriptor actúa sobre la representación Python. Para queries directas sobre la columna (ej: `User.email == valor`), SQLAlchemy compara el texto cifrado — no es buscable. La alternativa es un hybrid method/property separado. |
| **R3**: `display_name` usado en JWT roles claim (C-03 lo incluye en UserInfo) requiere migración de schema | El schema `UserInfo` (auth.py) se actualiza para quitar `display_name` y agregar `nombre`, `apellidos`, `display_name` como property derivada. El JWT no lleva display_name, solo user_id + tenant_id. |
| **R4**: La migración 008 modifica columnas existentes de `user` — la tabla puede tener datos en producción | La migración agrega columnas con `nullable=True` para campos nuevos y dropea `display_name`/`roles` (roles ya dropeado en DB). Los valores existentes de `email`, `password_hash`, `totp_secret`, `totp_enabled` se preservan. No hay transformación de datos destructiva. |
| **R5**: Regla de unicidad `(tenant_id, email)` puede fallar si hay emails duplicados preexistentes en DB | Previo a la migración, ejecutar script de deduplicación o notificar al ADMIN. El diseño asume que no hay duplicados (el modelo actual ya tiene `UniqueConstraint` sobre email+tenant). |

## Migration Plan

### Forward (008_usuarios_asignaciones.py)

1. **Alter table `user`**:
   - Agregar columnas: `nombre VARCHAR(255)`, `apellidos VARCHAR(255)`, `dni VARCHAR(512)` (cifrado), `cuil VARCHAR(512)` (cifrado), `cbu VARCHAR(512)` (cifrado), `alias_cbu VARCHAR(512)` (cifrado), `banco VARCHAR(255)`, `regional VARCHAR(255)`, `legajo VARCHAR(100)`, `legajo_profesional VARCHAR(100)`, `facturador BOOLEAN`, `activo BOOLEAN`
   - Dropear columna `display_name`
   - Dropear columna `roles` (por si acaso, verificar que ya no existe)
   - Migrar datos: `email` existente ya debe estar cifrado (de C-03) — se preserva

2. **Crear tabla `asignacion`**:
   - `id UUID PK`
   - `tenant_id UUID FK → tenant.id`
   - `usuario_id UUID FK → user.id NOT NULL`
   - `rol_id UUID FK → rol.id NOT NULL`
   - `materia_id UUID FK → materia.id NULL`
   - `carrera_id UUID FK → carrera.id NULL`
   - `cohorte_id UUID FK → cohorte.id NULL`
   - `comisiones JSONB NOT NULL DEFAULT '[]'`
   - `responsable_id UUID FK → user.id NULL`
   - `desde DATE NOT NULL`
   - `hasta DATE NULL`
   - `created_at`, `updated_at`, `deleted_at`

3. **Índices**: `(tenant_id, usuario_id)`, `(tenant_id, rol_id)`, `(tenant_id, materia_id)` para queries comunes

### Rollback (downgrade)

1. Dropear tabla `asignacion`
2. Re-agregar `display_name VARCHAR(255)` poblado con concatenación de nombre+apellidos existentes
3. Re-agregar columna `roles JSONB` (vacía)
4. Dropear columnas: dni, cuil, cbu, alias_cbu, banco, regional, legajo, legajo_profesional, facturador, activo, nombre, apellidos

## Open Questions

- **OQ1 (D9)**: ¿Se necesita un índice de búsqueda para email cifrado? Para el flujo de login, `get_by_email` descifra cada email del tenant en memoria. Con decenas de usuarios esto es aceptable. Con cientos, puede degradarse. Si es necesario, se agrega una columna `email_hash TEXT UNIQUE` con HMAC-SHA256 del email para lookup O(1). Decisión: no implementar ahora, monitorear performance.
- **OQ2**: ¿Se debe migrar `usuario_rol` a `asignacion` en esta migración? Decisión: NO. La tabla `usuario_rol` se conserva como histórica. Los datos existentes no tienen contexto académico (materia/carrera/cohorte) que Asignacion requiere.
- **OQ3**: ¿Se requiere audit log para ABM de usuarios/asignaciones? Sí, por regla dura "todo audita". El audit de estas operaciones se implementa como parte de C-05 (ya disponible). Los eventos relevantes: `USUARIO_CREAR`, `USUARIO_MODIFICAR`, `ASIGNACION_CREAR`, `ASIGNACION_MODIFICAR`.
