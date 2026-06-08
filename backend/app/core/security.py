import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import Settings
from app.core.exceptions import EncryptionError


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
