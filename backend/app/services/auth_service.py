import hashlib
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from app.core.exceptions import (
    ChallengeExpiredError,
    InvalidCredentialsError,
    RateLimitExceededError,
    TokenExpiredError,
    TwoFactorInvalidError,
)
from app.core.rate_limiter import RateLimiterProtocol
from app.core.security import (
    create_access_token,
    decrypt,
    encrypt,
    generate_totp_secret,
    generate_totp_uri,
    hash_password,
    verify_access_token,
    verify_password,
    verify_totp,
)
from app.models.password_reset_token import PasswordResetToken
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.core.config import Settings


@dataclass
class LoginResult:
    access_token: str | None = None
    refresh_token: str | None = None
    requires_2fa: bool = False
    challenge_token: str | None = None


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str


@dataclass
class TwoFactorEnrollResult:
    secret: str
    uri: str


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        rate_limiter: RateLimiterProtocol,
    ) -> None:
        self._user_repo = user_repository
        self._rt_repo = refresh_token_repository
        self._rate_limiter = rate_limiter
        self._settings = Settings()

    async def login(
        self,
        email: str,
        password: str,
        tenant_id: uuid.UUID,
        ip: str,
    ) -> LoginResult:
        rate_key = f"login:{ip}:{email}"
        allowed = await self._rate_limiter.check(rate_key)
        if not allowed:
            raise RateLimitExceededError("Demasiados intentos de login. Intente de nuevo en 60 segundos.")

        user = await self._user_repo.get_by_email(email, tenant_id)
        if user is None:
            raise InvalidCredentialsError("Email o contraseña incorrectos.")

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Email o contraseña incorrectos.")

        await self._rate_limiter.reset(rate_key)

        if user.totp_enabled:
            challenge = create_access_token(
                user_id=user.id,
                tenant_id=tenant_id,
                roles=user.roles,
                expires_delta=timedelta(minutes=5),
            )
            return LoginResult(requires_2fa=True, challenge_token=challenge)

        access = create_access_token(
            user_id=user.id,
            tenant_id=tenant_id,
            roles=user.roles,
        )
        refresh_raw = await self._emit_refresh_token(user.id, tenant_id)
        return LoginResult(access_token=access, refresh_token=refresh_raw)

    async def complete_2fa_login(
        self,
        challenge_token: str,
        totp_code: str,
    ) -> LoginResult:
        try:
            payload = verify_access_token(challenge_token)
        except (TokenExpiredError, InvalidCredentialsError) as exc:
            raise ChallengeExpiredError("Challenge token expirado o inválido.") from exc

        user_id = uuid.UUID(payload["sub"])
        tenant_id = uuid.UUID(payload["tenant_id"])

        user = await self._user_repo.get(user_id)
        if user is None or user.totp_secret is None:
            raise InvalidCredentialsError("Usuario no encontrado o 2FA no configurado.")

        decrypted_secret = decrypt(user.totp_secret)
        if not verify_totp(decrypted_secret, totp_code):
            raise TwoFactorInvalidError("Código TOTP inválido.")

        access = create_access_token(
            user_id=user.id,
            tenant_id=tenant_id,
            roles=user.roles,
        )
        refresh_raw = await self._emit_refresh_token(user.id, tenant_id)
        return LoginResult(access_token=access, refresh_token=refresh_raw)

    async def refresh(self, refresh_token_raw: str, user_id: uuid.UUID) -> TokenPair:
        token_hash = hashlib.sha256(refresh_token_raw.encode()).hexdigest()
        stored = await self._rt_repo.get_by_hash(token_hash)
        if stored is None:
            raise InvalidCredentialsError("Refresh token inválido.")

        if stored.revoked_at is not None:
            await self._rt_repo.revoke_all_for_user(user_id)
            raise InvalidCredentialsError(
                "Refresh token reutilizado — todas las sesiones fueron revocadas por seguridad.",
            )

        if stored.expires_at < datetime.now(timezone.utc):
            raise InvalidCredentialsError("Refresh token expirado.")

        access = create_access_token(
            user_id=stored.user_id,
            tenant_id=stored.tenant_id,
            roles=[],  # TODO: fetch from user in C-04 when RBAC exists
        )
        await self._rt_repo.revoke(stored)
        refresh_raw = await self._emit_refresh_token(stored.user_id, stored.tenant_id)

        return TokenPair(access_token=access, refresh_token=refresh_raw)

    async def logout(self, refresh_token_raw: str, user_id: uuid.UUID) -> None:
        token_hash = hashlib.sha256(refresh_token_raw.encode()).hexdigest()
        stored = await self._rt_repo.get_by_hash(token_hash)
        if stored is not None and stored.revoked_at is None:
            await self._rt_repo.revoke(stored)

    async def forgot(self, email: str, tenant_id: uuid.UUID) -> None:
        user = await self._user_repo.get_by_email(email, tenant_id)
        if user is None:
            return

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        reset_token = PasswordResetToken(
            token_hash=token_hash,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        )
        self._user_repo._session.add(reset_token)
        await self._user_repo._session.flush()

    async def reset(self, token_raw: str, new_password: str) -> None:
        token_hash = hashlib.sha256(token_raw.encode()).hexdigest()
        from sqlalchemy import select

        stmt = select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
        result = await self._user_repo._session.execute(stmt)
        stored = result.scalar_one_or_none()

        if stored is None:
            raise InvalidCredentialsError("Token de recuperación inválido.")

        if stored.used_at is not None:
            raise InvalidCredentialsError("Token de recuperación ya utilizado.")

        if stored.expires_at < datetime.now(timezone.utc):
            raise InvalidCredentialsError("Token de recuperación expirado.")

        user = await self._user_repo.get(stored.user_id)
        if user is None:
            raise InvalidCredentialsError("Usuario no encontrado.")

        user.password_hash = hash_password(new_password)
        stored.used_at = datetime.now(timezone.utc)
        await self._user_repo._session.flush()

    async def enroll_2fa(self, user_id: uuid.UUID) -> TwoFactorEnrollResult:
        user = await self._user_repo.get(user_id)
        if user is None:
            raise InvalidCredentialsError("Usuario no encontrado.")

        secret = generate_totp_secret()
        encrypted = encrypt(secret)
        user.totp_secret = encrypted
        await self._user_repo._session.flush()

        uri = generate_totp_uri(secret, user.email, self._settings.totp_issuer)
        return TwoFactorEnrollResult(secret=secret, uri=uri)

    async def verify_2fa(self, user_id: uuid.UUID, totp_code: str) -> None:
        user = await self._user_repo.get(user_id)
        if user is None or user.totp_secret is None:
            raise InvalidCredentialsError("Usuario no encontrado o 2FA no configurado.")

        decrypted = decrypt(user.totp_secret)
        if not verify_totp(decrypted, totp_code):
            raise TwoFactorInvalidError("Código TOTP inválido.")

        user.totp_enabled = True
        await self._user_repo._session.flush()

    async def get_2fa_status(self, user_id: uuid.UUID) -> bool:
        user = await self._user_repo.get(user_id)
        if user is None:
            raise InvalidCredentialsError("Usuario no encontrado.")
        return user.totp_enabled

    async def _emit_refresh_token(self, user_id: uuid.UUID, tenant_id: uuid.UUID) -> str:
        raw_token = secrets.token_urlsafe(48)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        refresh = RefreshToken(
            token_hash=token_hash,
            user_id=user_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=self._settings.refresh_token_expire_days),
        )
        refresh.tenant_id = tenant_id
        await self._rt_repo.create(refresh)
        return raw_token
