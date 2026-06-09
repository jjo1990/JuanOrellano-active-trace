import base64
import os
import uuid
from datetime import datetime, timedelta, timezone

import pyotp
from argon2 import PasswordHasher as _PasswordHasher
from argon2.exceptions import VerificationError as _VerificationError
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from jose import jwt as _jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError

from app.core.config import Settings
from app.core.exceptions import EncryptionError, TokenExpiredError, TokenInvalidError

_ph = _PasswordHasher()


# ── AES-256-GCM ─────────────────────────────────────────────────────


def _get_key(key: bytes | None = None) -> bytes:
    if key is not None:
        if len(key) != 32:
            msg = f"Key must be exactly 32 bytes, got {len(key)}"
            raise EncryptionError(msg)
        return key
    key_str = Settings().encryption_key
    key_bytes = key_str.encode("utf-8")
    if len(key_bytes) != 32:
        msg = f"ENCRYPTION_KEY must be exactly 32 bytes, got {len(key_bytes)}"
        raise EncryptionError(msg)
    return key_bytes


def encrypt(plaintext: str, key: bytes | None = None) -> str:
    """Cifra texto plano con AES-256-GCM.

    Formato de salida: base64(nonce(12) || ciphertext(N) || tag(16)).
    """
    key_bytes = _get_key(key)
    aesgcm = AESGCM(key_bytes)
    nonce = os.urandom(12)
    try:
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    except Exception as exc:
        msg = "Encryption failed"
        raise EncryptionError(msg) from exc
    return base64.b64encode(nonce + ciphertext).decode("ascii")


def decrypt(ciphertext_b64: str, key: bytes | None = None) -> str:
    """Descifra un string en formato base64(nonce || ciphertext || tag)."""
    key_bytes = _get_key(key)
    aesgcm = AESGCM(key_bytes)
    try:
        data = base64.b64decode(ciphertext_b64)
    except Exception as exc:
        msg = "Invalid base64 ciphertext"
        raise EncryptionError(msg) from exc

    if len(data) < 12 + 16:
        msg = "Ciphertext too short — missing nonce or tag"
        raise EncryptionError(msg)

    nonce = data[:12]
    ciphertext = data[12:]

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as exc:
        msg = "Decryption failed — key mismatch or corrupted ciphertext"
        raise EncryptionError(msg) from exc

    return plaintext.decode("utf-8")


# ── Argon2id ────────────────────────────────────────────────────────


def hash_password(plain: str) -> str:
    return _ph.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _ph.verify(hashed, plain)
    except _VerificationError:
        return False


# ── JWT ─────────────────────────────────────────────────────────────


def create_access_token(
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    roles: list[str],
    expires_delta: timedelta | None = None,
) -> str:
    settings = Settings()
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "roles": roles,
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return _jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def verify_access_token(token: str) -> dict:
    settings = Settings()
    try:
        return _jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except ExpiredSignatureError as exc:
        raise TokenExpiredError("Token expirado") from exc
    except (JWTClaimsError, Exception) as exc:
        raise TokenInvalidError("Token inválido") from exc


# ── TOTP ────────────────────────────────────────────────────────────


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def verify_totp(secret: str, token: str) -> bool:
    return pyotp.TOTP(secret).verify(token)


def generate_totp_uri(secret: str, email: str, issuer: str) -> str:
    return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)
