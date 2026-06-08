## Why

C-01 dejó el esqueleto de FastAPI con conexión async a PostgreSQL, logging estructurado, OpenTelemetry y el tooling de contenedores. Pero el sistema todavía no tiene modelo de datos. Sin las entidades base — Tenant, el mixin de PK/tenant_id/soft-delete y un Repository genérico que filtre por tenant por defecto — ningún change posterior (C-03 auth, C-04 RBAC, C-06 estructura académica) puede escribir una línea de lógica de negocio. C-02 es la segunda pieza del camino crítico.

## What Changes

- **Modelo Tenant**: entidad raíz que representa una institución. Campos: `id` (UUID), `nombre`, `slug` (único, para URLs/API), `config` (JSONB con settings del tenant: idioma, brand, umbrales default), `estado` (activo/inactivo), timestamps de soft delete. Es la primera entidad del sistema — sin Tenant no existen las demás.
- **BaseModelMixin**: mixin declarativo de SQLAlchemy que toda entidad hereda. Provee `id` (UUID, PK, generado con `uuid4()` del lado app), `tenant_id` (FK → Tenant, nullable solo para la entidad Tenant misma), `created_at`, `updated_at` (auto-set), `deleted_at` (nullable, soft delete).
- **Generic Repository** en `repositories/base.py`: clase abstracta genérica con CRUD básico. **Toda query incluye `tenant_id` como filtro obligatorio** — no existe método sin scope de tenant. Los métodos `get`, `list`, `create`, `update`, `soft_delete` operan siempre dentro del tenant. `list` excluye registros con `deleted_at IS NOT NULL` por defecto.
- **AES-256 encryption utility** en `core/security.py`: reemplaza el placeholder que dejó C-01. Implementa `encrypt(plaintext: str) -> str` y `decrypt(ciphertext: str) -> str` usando AES-256-GCM con clave de 32 bytes desde `ENCRYPTION_KEY`. Incluye manejo de nonce/authentication tag (formato: nonce\|ciphertext\|tag, base64). Es la utilidad que usarán todas las entidades con atributos `[cifrado]`.
- **Alembic migration 001**: crea la tabla `tenant`. Es la primera migración de schema del proyecto.
- **Tests de aislamiento multi-tenant**: un usuario del tenant A no puede leer/escribir datos del tenant B (prueba sobre Repository genérico). Test de soft delete (entity listada excluye soft-deleteadas). Test de round-trip de encryption. Test de timestamps (auto-set en create/update).
- **Actualización de `core/dependencies.py`**: añadir `get_tenant` como dependency que resuelve el `tenant_id` desde el contexto de autenticación. En C-02 es un placeholder funcional que esperará el JWT de C-03; por ahora puede devolver un tenant por defecto o mock para test.

**Slots que se llenan (reservados por C-01)**:
- `core/tenancy.py`: ✅ se implementa con modelo Tenant + BaseModelMixin.
- `core/security.py`: ✅ se implementa con AES-256 encrypt/decrypt (JWT y Argon2id quedan para C-03).
- `core/dependencies.py`: se agrega `get_tenant` (el placeholder ya existía con docstring).
- `exceptions.py`: se puebla con excepciones base del dominio (TenantNotFound, etc.).

## Capabilities

### New Capabilities

- `tenant-model`: entidad Tenant SQLAlchemy con UUID PK, slug único, JSONB config, soft delete.
- `base-mixin`: mixin declarativo `BaseModelMixin` con `id`, `tenant_id`, timestamps, soft delete. Toda entidad futura lo hereda.
- `repository`: clase `Repository[T]` genérica con CRUD y filtro obligatorio de `tenant_id`. `list` excluye soft-delete por defecto.
- `encryption`: utilidad AES-256-GCM para atributos `[cifrado]` (encrypt/decrypt con nonce+tag, base64).
- `migrations-001`: migración Alembic que crea `tenant` + índices (slug único, tenant_id para queries).
- `get-tenant-dependency`: dependency `get_tenant` que resuelve el tenant activo desde la sesión.

### Modified Capabilities

- `app-scaffold` (C-01): los placeholders `core/tenancy.py` y `core/security.py` se llenan con implementación real.
- `app-configuration` (C-01): se agrega validación de `ENCRYPTION_KEY` (exactamente 32 bytes) a `Settings`.

## Impact

- **Nuevo código**: `models/tenant.py`, `models/mixins.py`, `repositories/base.py`, implementación en `core/tenancy.py` y `core/security.py`, tests.
- **Schema de BD**: migración 001 crea `tenant` table.
- **Config**: `ENCRYPTION_KEY` ya existe en `.env.example` de C-01; se añade validación de longitud.
- **Dependencias**: se añade `cryptography` a `pyproject.toml` (AES-256-GCM).
- **Habilita**: C-03 (auth necesita Tenant para login), C-04 (RBAC necesita tenant scope), C-06 (estructura académica usa BaseModelMixin y Repository base).
- **Governance**: CRÍTICO — multi-tenancy es cimiento del sistema (ADR-002). Errores en aislamiento son fallas de seguridad. El diseño debe ser revisado antes de escribir código.
