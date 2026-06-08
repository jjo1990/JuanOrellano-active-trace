## 1. Modelo Tenant y BaseModelMixin (core/tenancy.py → models/)

- [x] 1.1 Crear `models/mixins.py` con `BaseModelMixin`:
  - `id`: Mapped[uuid.UUID] = Column(UUID, primary_key=True, default=uuid4)
  - `tenant_id`: Mapped[uuid.UUID | None] = Column(UUID, ForeignKey("tenant.id"), nullable=True)
  - `created_at`: Mapped[datetime] = Column(TIMESTAMP(timezone=True), server_default=func.now())
  - `updated_at`: Mapped[datetime] = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
  - `deleted_at`: Mapped[datetime | None] = Column(TIMESTAMP(timezone=True), nullable=True)

- [x] 1.2 Crear `models/tenant.py` con modelo `Tenant(BaseModelMixin)`:
  - `__tablename__` = "tenant"
  - `tenant_id = None` (es la única entidad sin FK a sí misma)
  - `nombre`: str (NOT NULL)
  - `slug`: str (NOT NULL, unique)
  - `config`: dict (JSONB, default={})
  - `estado`: str (default="activo")
  - `__table_args__`: Index en slug (unique), Index en estado

- [x] 1.3 Actualizar `models/__init__.py` para exportar `BaseModelMixin` y `Tenant`

- [x] 1.4 Mover o re-exportar `tenancy.py` como pasarela: `from app.models.tenant import Tenant; from app.models.mixins import BaseModelMixin`
  - Mantener el archivo `core/tenancy.py` como re-export para no romper referencias de C-01

## 2. AES-256-GCM encryption (core/security.py)

- [x] 2.1 (RED) Escribir `tests/test_encryption.py`:
  - Test round-trip: encrypt("hola") → ciphertext → decrypt(ciphertext) → "hola"
  - Test nonces diferentes para mismo plaintext
  - Test clave de 16 bytes es rechazada
  - Test ciphertext corrupto falla en decrypt

- [x] 2.2 (GREEN) Implementar en `core/security.py`:
  - `encrypt(plaintext: str, key: bytes | None = None) -> str`
  - `decrypt(ciphertext: str, key: bytes | None = None) -> str`
  - AES-256-GCM con `cryptography.hazmat`, nonce `os.urandom(12)`
  - Formato: `base64(nonce + ciphertext + tag)`
  - Validar que key tenga 32 bytes

- [x] 2.3 (TRIANGULATE) Agregar casos borde: string vacío, unicode (ñ, emoji), strings muy largos

## 3. Generic Repository (repositories/base.py)

- [x] 3.1 (RED) Escribir `tests/test_repository.py`:
  - Crear 2 tenants fixture + entidad de prueba
  - Test `get` retorna entidad del mismo tenant, None para otro tenant
  - Test `list` solo entidades del tenant
  - Test `create` asigna tenant_id automáticamente
  - Test `update` verifica tenant
  - Test `soft_delete` verifica tenant

- [x] 3.2 (GREEN) Implementar `repositories/base.py` con `Repository[T]`:
  - Constructor: `__init__(self, session: AsyncSession, tenant_id: uuid.UUID)`
  - `get(id) -> T | None`: SELECT con tenant_id + deleted_at IS NULL
  - `list(**filters) -> Sequence[T]`: SELECT con tenant_id + deleted_at IS NULL + filtros adicionales
  - `create(entity: T) -> T`: asigna tenant_id, add + flush/commit
  - `update(entity: T) -> T`: verifica tenant_id coincide, merge
  - `soft_delete(id) -> None`: SET deleted_at = now() WHERE id = X AND tenant_id = Y
  - Tipo genérico T bound a BaseModelMixin

- [x] 3.3 (TRIANGULATE) Agregar: list con filtros combinados, list retorna vacío si no hay entidades, update parcial

## 4. Alembic migration 001

- [x] 4.1 Crear `alembic/versions/001_create_tenant.py`:
  - up: CREATE TABLE tenant con UUID PK, slug UNIQUE, JSONB config, estado, timestamps
  - down: DROP TABLE tenant
  - Índices: UNIQUE en slug, INDEX en estado

- [x] 4.2 Verificar que `alembic upgrade head` ejecuta sin error contra PostgreSQL
- [x] 4.3 Verificar que `alembic downgrade -1` revierte correctamente

## 5. TDD Tests de tenancy y aislamiento

- [x] 5.1 (RED) Escribir `tests/test_tenancy.py`:
  - Test aislamiento multi-tenant: crear tenant A con entidad, repository de tenant B no la ve
  - Test soft delete: entidad con deleted_at ≠ None no aparece en list()
  - Test timestamps: created_at y updated_at se setean automáticamente

- [x] 5.2 (GREEN) Asegurar que los modelos implementan los requerimientos de aislamiento
- [x] 5.3 (TRIANGULATE) Agregar escenarios: soft delete + create con mismo ID en otro tenant, list con filtros + soft delete combinados

## 6. Dependencies y exceptions

- [x] 6.1 Agregar `get_tenant` en `core/dependencies.py`:
  - Por ahora es un resolver básico (mock/default tenant para desarrollo)
  - Documentar que C-03 reemplazará la resolución por JWT

- [x] 6.2 Poblar `core/exceptions.py`:
  - `TenantNotFoundError(Exception)` — tenant no existe o está inactivo
  - `EncryptionError(Exception)` — fallo en encrypt/decrypt
  - `RepositoryError(Exception)` — error genérico de repositorio

## 7. Config y dependencias

- [x] 7.1 Añadir `cryptography` a `backend/pyproject.toml`
- [x] 7.2 Añadir validación de `ENCRYPTION_KEY` (32 bytes) en `core/config.py`

## 8. Verificación final

- [x] 8.1 Ejecutar suite completa de tests (`pytest`) y confirmar verde
- [x] 8.2 Verificar `alembic upgrade head` y `alembic downgrade -1`
- [x] 8.3 Confirmar que ningún archivo `.py` supera 500 LOC
- [x] 8.4 Confirmar que todos los Pydantic schemas nuevos (si los hay) usan `extra='forbid'`
- [x] 8.5 Confirmar que no hay hard delete en ningún repository
