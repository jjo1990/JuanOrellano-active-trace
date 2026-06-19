## Context

C-01 dejó el esqueleto funcional: FastAPI arranca, health-check responde, sesión async a PostgreSQL funciona, `core/tenancy.py` y `core/security.py` existen como placeholders. Ahora hay que llenarlos.

El contrato de arquitectura (ADR-002, `docs/ARQUITECTURA.md §6`) es claro: **multi-tenancy row-level** con columna `tenant_id` en toda tabla, repositorios que filtran por tenant por defecto. También define AES-256 para PII sensible (`docs/ARQUITECTURA.md §5.4`). El modelo de datos (`knowledge-base/04_modelo_de_datos.md`) describe `[cifrado]` como convención para atributos sensibles.

C-02 implementa estos cimientos que C-01 reservó. Es **el primer cambio que toca seguridad y aislamiento** — governance CRÍTICO.

## Goals / Non-Goals

**Goals:**

- Implementar modelo `Tenant` con UUID PK, slug único (único en sistema), `config` JSONB, timestamps de soft delete.
- Implementar `BaseModelMixin` como mixin SQLAlchemy que toda entidad hereda: `id` (UUID, app-side con `uuid4()`), `tenant_id` (FK nullable solo para Tenant mismo), `created_at`, `updated_at`, `deleted_at`.
- Implementar clase genérica `Repository[T]` en `repositories/base.py` con métodos `get`, `list`, `create`, `update`, `soft_delete`. **Toda query incluye `tenant_id`** como filtro obligatorio. `list` excluye soft-deleteados por defecto.
- Implementar AES-256-GCM `encrypt`/`decrypt` en `core/security.py` con clave de 32 bytes, nonce aleatorio + authentication tag (formato: `base64(nonce || ciphertext || tag)`).
- Migration 001: tabla `tenant` con índices en `slug` (único) y `estado`.
- Dependency `get_tenant` que resuelve el tenant actual (para C-02 es funcional contra mock/test; en C-03 se conecta al JWT).
- Tests de aislamiento multi-tenant, soft delete, encryption round-trip, timestamps.

**Non-Goals:**

- Auth, JWT, Argon2id, hash de passwords (→ C-03).
- RBAC, matriz de permisos, `require_permission` (→ C-04).
- Entidades de negocio más allá de `Tenant` (Usuario, Materia, etc. → C-06+).
- Auditoría (AuditLog → C-05).
- Migraciones de datos o seed de tenants.

## Decisions

### D1 — Estrategia de tenant isolation: row-level (ADR-002 confirmado)

Se confirma row-level: columna `tenant_id` FK → `tenant.id` en toda tabla. Los repositories filtran por tenant en cada query. Database-per-tenant se reevalúa solo si un tenant exige aislamiento físico regulatorio.

**Alternativa descartada**: schema-per-tenant (un schema de PostgreSQL por tenant). Se descarta por complejidad operativa (migraciones N veces, pool de conexiones, backups) sin beneficio actual. ADR-002 ya cerró esta decisión.

### D2 — UUID generados on app side con uuid4()

Los IDs se generan en la aplicación con `uuid.uuid4()`, no con `gen_random_uuid()` de PostgreSQL. Esto permite:
- Crear entidades sin commit previo (útil en tests y en lógica transaccional compleja).
- Serializar y cachear objetos antes de persistirlos.
- Consistencia: la app controla el formato, no delegado al motor.

**Trade-off**: pérdida de monotonía (vs `uuid_v7` o secuencias). Aceptado: las PKs UUID no necesitan orden secuencial en este sistema. Si más adelante se requiere orden por creación, se usa `created_at`.

### D3 — Soft delete como mixin, no como herencia de tabla

El soft delete se implementa como **mixin declarativo**, no como tabla base con herencia. Cada entidad declara `deleted_at` como nullable y los repositorios filtran por defecto.

**Alternativa descartada**: tabla base `SoftDeleteMixin` con herencia joined-table. Se descarta porque añade JOINs innecesarios en cada query y complica el modelo de SQLAlchemy. Un mixin simple (columna + flag) es suficiente.

### D4 — AES-256-GCM con nonce aleatorio

Algoritmo: **AES-256-GCM** (modo Galois/Counter). Cada operación de encrypt genera un nonce aleatorio de 12 bytes. El ciphertext incluye autenticación: si el ciphertext se corrompe, `decrypt` falla. Formato de salida: `base64(nonce (12) || ciphertext (N) || tag (16))` → todo en un string manejable. La clave se lee de `ENCRYPTION_KEY` (32 bytes, configuración existente de C-01).

**Alternativa descartada**: AES-256-CBC. Se descarta porque no provee autenticación intrínseca (requiere HMAC aparte). GCM es el estándar actual para cifrado simétrico autenticado.

### D5 — Repository genérico con mandatory tenant scope

```python
class Repository[T: BaseModelMixin]:
    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None: ...

    async def get(self, id: UUID) -> T | None: ...       # WHERE id=X AND tenant_id=Y AND deleted_at IS NULL
    async def list(self, **filters) -> Sequence[T]: ...   # WHERE tenant_id=Y AND deleted_at IS NULL [+ filters]
    async def create(self, entity: T) -> T: ...           # SET tenant_id automáticamente
    async def update(self, entity: T) -> T: ...           # SOLO si tenant_id coincide
    async def soft_delete(self, id: UUID) -> None: ...   # SET deleted_at = now(), SOLO si tenant_id coincide
```

- `tenant_id` se inyecta en el constructor (no por parámetro por método) para garantizar que ningún método se olvide de filtrar.
- `list` excluye soft-deleteados por defecto.
- `create` SET `tenant_id` automáticamente desde el tenant inyectado.
- `update` y `soft_delete` verifican que el `tenant_id` coincida antes de operar (defense in depth).

### D6 — get_tenant dependency

```python
async def get_tenant(request: Request) -> UUID:
    ...
```

En C-02 esta dependency es funcional: intenta resolver el tenant desde la request. Como aún no hay JWT, se implementa con un tenant por defecto desde config (modo desarrollo) o se mockea en tests. El slot está documentado para que C-03 reemplace la resolución por el JWT verificado.

### D7 — TDD con base de datos real (no mock de DB)

Regla dura del proyecto: **tests con base de datos real**, nunca mock de SQLAlchemy/sesión. Los tests de C-02 usan PostgreSQL efímera (vía docker-compose test profile o base de test dedicada). Fixtures en `conftest.py`:
- `db_session`: sesión async contra la base de test, con rollback al final para no contaminar.
- `tenant_a` / `tenant_b`: dos tenants creados en la base de test para tests de aislamiento.

### D8 — Layout de archivos nuevos/modificados

```
backend/app/
├── core/
│   ├── tenancy.py          # ✅ LLENADO: Tenant model, BaseModelMixin
│   ├── security.py          # ✅ LLENADO: AES-256-GCM encrypt/decrypt
│   ├── dependencies.py      # ✅ MODIFICADO: se agrega get_tenant
│   └── exceptions.py        # ✅ LLENADO: TenantNotFound, EncryptionError
├── models/
│   ├── __init__.py           # ✅ MODIFICADO: exporta Tenant, BaseModelMixin
│   ├── tenant.py             # 🆕 Modelo Tenant SQLAlchemy
│   └── mixins.py             # 🆕 BaseModelMixin
├── repositories/
│   ├── __init__.py           # ✅ MODIFICADO
│   └── base.py               # 🆕 Repository[T] genérico
├── alembic/
│   └── versions/
│       └── 001_create_tenant.py  # 🆕 Primera migración
└── tests/
    ├── conftest.py           # ✅ MODIFICADO: fixtures tenant_a, tenant_b
    ├── test_tenancy.py       # 🆕 Test aislamiento multi-tenant + soft delete
    ├── test_repository.py    # 🆕 Test CRUD genérico con scope de tenant
    ├── test_encryption.py    # 🆕 Test AES-256 round-trip
    └── test_mixins.py        # 🆕 Test timestamps del mixin
```

No se modifica `backend/pyproject.toml` salvo para añadir `cryptography` (dependencia de AES-256-GCM). No se tocan `main.py`, routers, `config.py`, `database.py` ni docker-compose.

## Risks / Trade-offs

- **[Tenant como entidad sin slug único global]: puede haber colisión si dos instituciones quieren el mismo slug** → Mitigación: validación de unicidad con check en el repository antes de crear; si la institución quiere "university", se verifica que no exista. Slug se usa como identificador amigable, no como PK.
- **[UUIDs del lado app pueden generar colisiones teóricas]** → Mitigación: `uuid4()` con 122 bits aleatorios; riesgo de colisión despreciable (1 en 2^71 con 10^18 UUIDs). La app puede capturar `IntegrityError` como defensa adicional.
- **[AES-256-GCM nonce de 12 bytes: si se reusa nonce con misma clave, el cifrado se rompe]** → Mitigación: `os.urandom(12)` en cada encrypt. El nonce se almacena junto al ciphertext, no se deriva de un contador. Riesgo colisión ≈ 1 en 2^96.
- **[get_tenant sin JWT todavía (C-03)]** → Mitigación: en C-02 se implementa con un tenant default desde config/env para desarrollo. Los tests usan fixture que inyecta tenant específico. La integración real con JWT es tarea de C-03.
- **[Repository genérico puede ser demasiado rígido para casos complejos]** → Mitigación: el genérico implementa CRUD estándar. Los repositories de dominio (C-06+) heredan y agregan métodos específicos. No se fuerza a usar solo los métodos genéricos.

## Migration Plan

No hay migración de datos (primer schema de BD). Migration 001 se ejecuta con `alembic upgrade head` en el arranque o vía script de deploy. Rollback: `alembic downgrade -1` elimina la tabla `tenant`. No hay datos que preservar.

## Open Questions

- **¿Debe `tenant.slug` ser único global o solo en el sistema?** El diseño propone único global (como identificador amigable del tenant). Alternativa: delegar a un subdominio o UUID. Se resuelve en apply; la migración 001 ya define UNIQUE INDEX en slug.
- **¿Engine de test efímero vs base de test fija?** Recomendación: usar una base PostgreSQL vía docker-compose test profile o `DATABASE_URL_TEST`. Se decide en apply según el setup de CI.
- **¿`ENCRYPTION_KEY` en env de test debe ser fija (para tests deterministas) o variable?** Recomendación: fija en `.env.test` para tests deterministas de round-trip. Decisión menor.
