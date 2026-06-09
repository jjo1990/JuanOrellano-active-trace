## Why

C-02 estableció los cimientos de multi-tenancy (Tenant, BaseModelMixin, Repository genérico) pero el sistema aún no puede autenticar usuarios. Sin login, JWT ni resolución de identidad, ningún endpoint protegido puede operar. C-03 es la tercera pieza del camino crítico: habilita sesiones autenticadas, refresh rotation, 2FA TOTP opcional y recuperación de contraseña, cumpliendo ADR-001 (auth propio endurecido para MVP).

## What Changes

- **Modelo User**: entidad SQLAlchemy que representa a un usuario del sistema. Email único por tenant, password hasheado con Argon2id, 2FA secret (cifrado AES-256), soft delete. FK `tenant_id` obligatoria.
- **POST /api/auth/login**: valida email + password con Argon2id. Si el usuario tiene 2FA habilitado, emite un token parcial (2FA challenge) en lugar de la sesión completa. Rate limiting 5 intentos/60s por IP+email.
- **POST /api/auth/login/2fa**: completa el login con TOTP, emite access token (15min) + refresh token con rotación.
- **POST /api/auth/refresh**: rota el refresh token (el usado se invalida), emite nuevo par access+refresh.
- **POST /api/auth/logout**: revoca la sesión (invalida el refresh token).
- **2FA TOTP opcional por usuario**: enrolar (`POST /api/auth/2fa/enroll`), verificar (`POST /api/auth/2fa/verify`), estado (`GET /api/auth/2fa/status`). Datos cifrados AES-256 en reposo.
- **Password recovery**: `POST /api/auth/forgot` genera un token de un solo uso (expiración 30min) enviado por email; `POST /api/auth/reset` consume el token y actualiza el password.
- **Dependency `get_current_user`**: resuelve identidad (`user_id`), tenant (`tenant_id`) y roles desde JWT verificado. Es la base de toda autenticación posterior.
- **Dependency `get_tenant_from_jwt`**: reemplaza el placeholder de C-02 `get_tenant` con resolución real desde JWT.
- **Claims JWT mínimos**: `sub` (user_id UUID), `tenant_id` (UUID), `roles` (lista de strings), `exp` (timestamp). Sin permisos en el token.
- **Refresh token storage**: tabla `refresh_token` con hash del token, `user_id`, `tenant_id`, `expires_at`, `revoked_at` (soft revoke).
- **Password reset token**: tabla `password_reset_token` con token hash, `user_id`, `tenant_id`, `expires_at`, `used_at`.
- **Tests**: login OK/KO, refresh rotation (reuso invalida sesión), 2FA flow completo, password recovery one-time token, rate limit, identidad inmutable por parámetro.
- **Schema de BD**: migraciones 002 (User), 003 (refresh_token), 004 (password_reset_token).

**Slots que se llenan:**
- `core/security.py`: ✅ se añade JWT sign/verify, Argon2id hash/verify, TOTP generate/verify.
- `core/dependencies.py`: ✅ se reemplaza `get_tenant` placeholder por `get_current_user` y `get_tenant_from_jwt`.
- `core/tenancy.py`: no se modifica (ya completo desde C-02).

## Capabilities

### New Capabilities
- `user-model`: entidad User SQLAlchemy con email único por tenant, password Argon2id, 2FA secret cifrado, soft delete.
- `login-endpoint`: validación de credenciales con rate limiting, gate de 2FA, emisión de sesión JWT.
- `token-management`: JWT access token (15min) + refresh rotation, refresh token storage en BD, invalidation on reuse.
- `2fa-totp`: enrolar, verificar y consultar estado de TOTP 2FA por usuario. Secret cifrado AES-256.
- `password-recovery`: forgot (token one-time por email) + reset (consume token, actualiza password).
- `auth-dependencies`: `get_current_user` y `get_tenant_from_jwt` que resuelven identidad + tenant desde JWT verificado.
- `logout-endpoint`: revocación de refresh token, cierre de sesión.
- `rate-limiting`: middleware/guard de rate limiting 5 intentos/60s por IP+email en login.

### Modified Capabilities
- `get-tenant-dependency` (C-02): el placeholder `get_tenant` se reemplaza por `get_tenant_from_jwt` con resolución real.
- `app-security` (C-01): `core/security.py` se completa con JWT sign/verify y Argon2id.

## Impact

- **Nuevo código**: `models/user.py`, `models/refresh_token.py`, `models/password_reset_token.py`, `schemas/auth.py`, `repositories/user_repository.py`, `repositories/refresh_token_repository.py`, `services/auth_service.py`, `api/v1/routers/auth.py`, `core/security.py` (JWT + Argon2id + TOTP), `core/permissions.py` (matriz initial), `core/dependencies.py` (get_current_user, get_tenant_from_jwt), rate limiter utility, tests.
- **Schema de BD**: migraciones 002 (user), 003 (refresh_token), 004 (password_reset_token).
- **Config**: se añaden `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `JWT_ALGORITHM`, `TOTP_ISSUER` a Settings. `SECRET_KEY` ya existe desde C-01.
- **Dependencias**: se añaden `pyjwt`, `pyotp` a `pyproject.toml`. **No se necesita bcrypt ni passlib** — Argon2id va directo con `argon2-cffi` (ya incluido desde C-01).
- **Habilita**: C-04 (RBAC necesita `get_current_user`), C-05 (auditoría necesita identidad resuelta), C-21 (frontend necesita login y refresh).
- **Governance**: CRÍTICO — auth es la puerta de entrada al sistema. Errores en autenticación son fallas de seguridad. El diseño debe ser revisado antes de escribir código.
