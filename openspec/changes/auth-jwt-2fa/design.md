## Context

C-02 dejó los cimientos de multi-tenancy: modelo Tenant, BaseModelMixin, Repository genérico con scope de tenant obligatorio, AES-256-GCM, y un placeholder `get_tenant` en dependencies. C-03 construye sobre esos cimientos el sistema de autenticación completo:

- **User model** con Argon2id, email único por tenant, 2FA secret cifrado.
- **JWT access token** (15min) + **refresh rotation** (un refresh usado se invalida).
- **2FA TOTP opcional** por usuario, con gate entre validación de credenciales y emisión de sesión.
- **Rate limiting** 5 intentos/60s por IP+email en login.
- **Password recovery** con token de un solo uso por email.
- **Dependencies** `get_current_user` y `get_tenant_from_jwt` que reemplazan el placeholder de C-02.

El contrato de arquitectura es claro: ADR-001 (auth propio endurecido), `docs/ARQUITECTURA.md §5` (JWT, Argon2id, 2FA, refresh rotation), `knowledge-base/03_actores_y_roles.md` (identidad desde sesión, RBAC). Los flujos están detallados en `knowledge-base/07_flujos_principales.md §FL-01`.

**Governance**: CRÍTICO — auth es la puerta de entrada. Errores son fallas de seguridad.

## Goals / Non-Goals

**Goals:**

- Implementar modelo `User` con email único por tenant, password Argon2id, 2FA secret (cifrado AES-256), timestamps, soft delete.
- Endpoint `POST /api/auth/login`: validación de credenciales + rate limiting + gate de 2FA.
- Endpoint `POST /api/auth/login/2fa`: verificación TOTP → emisión de par access+refresh.
- Endpoint `POST /api/auth/refresh`: rotación de refresh (el usado se invalida), nuevo par.
- Endpoint `POST /api/auth/logout`: revocación de refresh token.
- Endpoint `POST /api/auth/2fa/enroll`: generar y devolver secret TOTP (QR URI), guardar cifrado.
- Endpoint `POST /api/auth/2fa/verify`: verificar un TOTP contra el secret, habilitar 2FA.
- Endpoint `GET /api/auth/2fa/status`: consultar si el usuario tiene 2FA habilitado.
- Endpoint `POST /api/auth/forgot`: generar token one-time (exp 30min), enviar por email.
- Endpoint `POST /api/auth/reset`: validar token, actualizar password.
- Dependency `get_current_user`: resuelve `user_id`, `tenant_id`, `roles` desde JWT verificado.
- Dependency `get_tenant_from_jwt`: reemplaza placeholder de C-02.
- Rate limiter: 5 intentos/60s por (IP + email) en login.
- Tres migraciones: 002 (user), 003 (refresh_token), 004 (password_reset_token).
- Tests: login OK/KO, refresh rotation (reuso invalida), 2FA flow completo, recovery one-time, rate limit, identidad inmutable.

**Non-Goals:**

- RBAC fino con `require_permission` (→ C-04).
- Audit log de acciones de auth (→ C-05).
- Frontend de login/session (→ C-21).
- Moodle SSO (→ Fase 2, ADR-001).
- Impersonation (→ ADR-004, se define durante desarrollo).
- Catálogo de roles administrable por tenant (datos, no código — se define en C-04).
- Email service real (se mockea en tests; el worker de comunicaciones es C-09+).

## Decisions

### D1 — Argon2id directo con argon2-cffi (SIN passlib)

Se usa `argon2-cffi` directamente, no passlib. La dependencia `argon2-cffi` YA existe en `pyproject.toml` desde C-01.

```python
from argon2 import PasswordHasher
ph = PasswordHasher()
hash = ph.hash("mi_password")      # → hasheo
ph.verify(hash, "mi_password")     # → True/False
```

**⚠️ Error corregido**: el diseño original decía `passlib[bcrypt]` con scheme argon2 — eso es INCORRECTO. `passlib[bcrypt]` instala bcrypt, no argon2. Usar `argon2-cffi` directamente elimina una capa de abstracción innecesaria, reduce dependencias y va directo al estándar OWASP.

**Alternativa descartada**: `passlib[argon2]` (válido pero agrega una abstracción superflua — `argon2-cffi` ya tiene API directa y testada). `bcrypt` solo (más rápido pero menos resistente a ataques GPU/ASIC).

### D2 — JWT con pyjwt, sin authlib ni fastapi-jwt-auth

Se usa `PyJWT` directamente. Firma con HS256 sobre `SECRET_KEY` (≥32 chars, ya existe desde C-01).

```python
import jwt
payload = {"sub": str(user_id), "tenant_id": str(tenant_id), "roles": roles, "exp": exp}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

**Alternativa descartada**: `fastapi-jwt-auth` o `authlib` — añaden dependencias y abstracciones innecesarias para la simplicidad del modelo. PyJWT da control total sobre claims y manejo de errores.

### D3 — Refresh token storage en BD con hash del token

El refresh token se almacena en la tabla `refresh_token` como hash SHA-256 (no texto plano). Esto es fundamental: si alguien roba la BD, no puede usar refresh tokens.

- Al emitir: `token_raw = secrets.token_urlsafe(48)` → hash → guarda hash + expiración + user_id + tenant_id.
- Al refresh: recibe `token_raw` → hashea → busca en BD → si existe y no está revocado → rota (invalida el viejo, crea uno nuevo).
- Si un refresh usado se reenvía (reuse attack), se detecta porque el hash ya existe con `revoked_at` seteado → se revocan TODAS las sesiones del usuario (medida de seguridad).

**Alternativa descartada**: almacenar el token mismo en la BD (riesgo de exposición). JWT como refresh (no se puede revocar). Stateless refresh sin BD (vulnerable a theft sin detección).

### D4 — 2FA gate: two-step login flow

El flujo de login con 2FA es de dos pasos:
1. `POST /api/auth/login` → credenciales OK + usuario tiene 2FA → responde con `{"requires_2fa": true, "challenge_token": "..."}` (token JWT parcial, 5min de vida, solo para completar 2FA). Si no tiene 2FA → emite sesión completa.
2. `POST /api/auth/login/2fa` → recibe challenge_token + TOTP → verifica → emite sesión completa.

**Alternativa descartada**: pedir 2FA después de emitir sesión completa (el usuario ya tiene acceso antes de 2FA, rompe el gate de seguridad). Usar un endpoint único con campo `2fa_code` opcional (no permite distinguir entre "no tiene 2FA" y "no lo ingresó" sin exponer información).

### D5 — Rate limiting en memoria con Protocol para swap a Redis

Se implementa rate limiting siguiendo un **Protocol** (PEP 544) que permite cambiar la implementación sin modificar el servicio. La implementación concreta para MVP usa un dict en memoria + ventana deslizante.

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class RateLimiterProtocol(Protocol):
    async def check(self, key: str) -> bool: ...
    async def reset(self, key: str) -> None: ...

class InMemoryRateLimiter:
    def __init__(self, max_attempts: int = 5, window_seconds: int = 60):
        self._store: dict[str, list[float]] = defaultdict(list)
    
    async def check(self, key: str) -> bool:  # True = allowed
        now = time.time()
        window_start = now - self.window_seconds
        self._store[key] = [t for t in self._store[key] if t > window_start]
        if len(self._store[key]) >= self.max_attempts:
            return False
        self._store[key].append(now)
        return True
    
    async def reset(self, key: str) -> None:
        self._store.pop(key, None)
```

**Punto de extensión**: cuando se necesite multi-worker, se implementa `RedisRateLimiter(RateLimiterProtocol)` y se reemplaza en la inyección de dependencias. El `auth_service` depende del Protocol, nunca de la implementación concreta.

Key compuesta: `f"login:{ip}:{email}"`.

**Alternativa descartada**: Redis para MVP (overhead operativo sin beneficio con un worker). Clase sin Protocol (obliga a cambiar el service cuando se quiera swap).

### D6 — TOTP con pyotp, secret cifrado AES-256

Se usa `pyotp` para generar y verificar TOTP. El secret se almacena cifrado con AES-256-GCM (utilidad de C-02). Al enrollar, se genera `pyotp.random_base32()` → se cifra y guarda. Al verificar, se descifra y se pasa a `pyotp.TOTP(secret).verify(token)`.

```python
secret = pyotp.random_base32()
encrypted = encrypt(secret)
# guardar encrypted en user.totp_secret
# para verificar:
decrypted = decrypt(user.totp_secret)
valid = pyotp.TOTP(decrypted).verify(token)
```

### D7 — Password reset token: one-time con hash en BD

Similar a refresh tokens: `secrets.token_urlsafe(32)` → hash SHA-256 → guarda hash + user_id + expires_at + used_at. El link enviado por email contiene el token raw. Al reset, se hashea, se busca, se verifica que no esté usado ni expirado, se actualiza password y se marca como usado.

### D8 — Layout de archivos nuevos/modificados

```
backend/
├── app/
│   ├── api/v1/routers/
│   │   └── auth.py                    # 🆕 Endpoints de auth
│   ├── core/
│   │   ├── security.py                # ✅ MODIFICADO: se añade JWT + Argon2id + TOTP
│   │   ├── dependencies.py            # ✅ MODIFICADO: get_current_user, get_tenant_from_jwt
│   │   ├── rate_limiter.py            # 🆕 Rate limiter in-memory
│   │   └── exceptions.py              # ✅ MODIFICADO: AuthError, InvalidCredentials, etc.
│   ├── models/
│   │   ├── __init__.py                # ✅ MODIFICADO: exporta User, RefreshToken, PasswordResetToken
│   │   ├── user.py                    # 🆕 Modelo User SQLAlchemy
│   │   ├── refresh_token.py           # 🆕 Modelo RefreshToken
│   │   └── password_reset_token.py    # 🆕 Modelo PasswordResetToken
│   ├── schemas/
│   │   └── auth.py                    # 🆕 Schemas Pydantic: LoginRequest, TokenResponse, etc.
│   ├── repositories/
│   │   ├── user_repository.py         # 🆕 UserRepository(Repository[User])
│   │   └── refresh_token_repository.py # 🆕 RefreshTokenRepository(Repository[RefreshToken])
│   └── services/
│       └── auth_service.py            # 🆕 Lógica de negocio: login, refresh, 2fa, recovery
├── alembic/
│   └── versions/
│       ├── 002_create_user.py         # 🆕 Migración: tabla user
│       ├── 003_create_refresh_token.py# 🆕 Migración: tabla refresh_token
│       └── 004_create_password_reset_token.py # 🆕 Migración: tabla password_reset_token
└── tests/
    ├── conftest.py                    # ✅ MODIFICADO: fixtures user, refresh_token
    ├── test_login.py                  # 🆕 Test login OK/KO + rate limit
    ├── test_refresh.py                # 🆕 Test refresh rotation + reuse attack
    ├── test_2fa.py                    # 🆕 Test 2FA enroll/verify/gate
    ├── test_recovery.py               # 🆕 Test forgot/reset one-time token
    └── test_auth_deps.py              # 🆕 Test get_current_user, identidad inmutable
```

No se modifica `main.py` salvo para registrar el router de auth. No se tocan `config.py`, `database.py`, `models/mixins.py`, `models/tenant.py`, `repositories/base.py`.

## Risks / Trade-offs

- **[Rate limiter en memoria no escala a multi-worker]**: En MVP con un worker no hay problema. Cuando se escale a multi-worker, se implementa `RedisRateLimiter(RateLimiterProtocol)` y se reemplaza en la inyección de dependencias. El Protocol garantiza que ningún código del service necesita cambios.
- **[Reuse attack de refresh token revoca TODAS las sesiones]**: Es la defensa recomendada por RFC. Si un atacante roba un refresh y el usuario legítimo lo usa primero, el atacante queda invalidado. Si el atacante lo usa primero, el legítimo pierde su sesión al intentar refresh — pero el usuario puede re-login. Trade-off aceptado por seguridad.
- **[2FA gate expone metadata (saber que un usuario tiene 2FA)]**: El challenge token se emite SOLO cuando las credenciales son válidas. Un atacante sin credenciales válidas no puede saber si el usuario tiene 2FA. Para un atacante con credenciales válidas pero sin 2FA, la existencia de 2FA ya no es información útil.
- **[TOTP sin recovery codes en MVP]**: Si un usuario pierde acceso a su TOTP app, necesita contactar al ADMIN para deshabilitar 2FA. Recovery codes se añaden en futura iteración. **Aceptado para MVP.**
- **[Email service mockeado en tests]**: El envío real de emails es responsabilidad del worker de comunicaciones (C-09+). En C-03, `forgot` encola el envío o llama a un mock.
- **[Password reset token en BD puede crecer sin límite]**: Se añade cleanup periódico (TTL index en `expires_at` + job de limpieza) o se planifica para futura iteración.

## Migration Plan

No hay migración de datos (primer schema de auth). Migraciones 002-004 se ejecutan con `alembic upgrade head`. Rollback: `alembic downgrade -3` revierte las tres tablas. No hay datos que preservar.

Secuencia:
1. Escribir modelos (User, RefreshToken, PasswordResetToken)
2. Generar migraciones Alembic
3. Implementar `core/security.py` (JWT + Argon2id)
4. Implementar `core/rate_limiter.py`
5. Implementar repositories
6. Implementar schemas Pydantic
7. Implementar `auth_service.py`
8. Implementar router `auth.py`
9. Actualizar `core/dependencies.py`
10. Tests TDD (RED → GREEN → TRIANGULATE) en ese orden: login → refresh → 2FA → recovery → auth deps → rate limit

## Open Questions

- **¿Email service real o mock en MVP?** El diseño propone mock/dummy para C-03; el worker de comunicaciones (C-09) implementa el envío real. Confirmar si el equipo quiere integrar sendmail/SMTP ya en C-03.
- **¿Recovery codes para 2FA?** El diseño no los incluye (MVP scope). Confirmar si se requieren antes de cerrar este change.
- **¿Refresh token cleanup automático?** Se puede añadir un job periódico o un TTL index en PostgreSQL para cleanup automático. Decisión menor.
