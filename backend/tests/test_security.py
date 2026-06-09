import uuid
from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JOSEError

from app.core.config import Settings


class TestJWT:
    def test_sign_and_verify(self):
        user_id = uuid.uuid4()
        tenant_id = uuid.uuid4()
        roles = ["alumno"]
        settings = Settings()
        payload = {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "roles": roles,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        }
        token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
        decoded = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        assert decoded["sub"] == str(user_id)
        assert decoded["tenant_id"] == str(tenant_id)
        assert decoded["roles"] == roles

    def test_invalid_signature_rejected(self):
        settings = Settings()
        payload = {
            "sub": str(uuid.uuid4()),
            "tenant_id": str(uuid.uuid4()),
            "roles": [],
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        }
        token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
        with pytest.raises(JOSEError):
            jwt.decode(token, "x" * 32, algorithms=[settings.jwt_algorithm])

    def test_expired_token_rejected(self):
        settings = Settings()
        payload = {
            "sub": str(uuid.uuid4()),
            "tenant_id": str(uuid.uuid4()),
            "roles": [],
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        }
        token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
        with pytest.raises(ExpiredSignatureError):
            jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])

    def test_token_without_claims(self):
        settings = Settings()
        payload = {"exp": datetime.now(timezone.utc) + timedelta(minutes=15)}
        token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
        decoded = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        assert "sub" not in decoded

    def test_malformed_token_rejected(self):
        settings = Settings()
        with pytest.raises(JOSEError):
            jwt.decode("not-a-jwt-token", settings.secret_key, algorithms=[settings.jwt_algorithm])


class TestArgon2id:
    def test_hash_and_verify(self):
        from argon2 import PasswordHasher

        ph = PasswordHasher()
        password = "securePass123!"
        hashed = ph.hash(password)
        assert hashed != password
        assert ph.verify(hashed, password) is True

    def test_wrong_password_fails(self):
        from argon2 import PasswordHasher

        ph = PasswordHasher()
        hashed = ph.hash("securePass123!")
        with pytest.raises(Exception):
            ph.verify(hashed, "wrongPassword")

    def test_unicode_password(self):
        from argon2 import PasswordHasher

        ph = PasswordHasher()
        password = "contraseñañandú😊"
        hashed = ph.hash(password)
        assert ph.verify(hashed, password) is True


class TestTOTP:
    def test_generate_and_verify(self):
        import pyotp

        secret = pyotp.random_base32()
        token = pyotp.TOTP(secret).now()
        assert pyotp.TOTP(secret).verify(token) is True

    def test_valid_window(self):
        import pyotp

        secret = pyotp.random_base32()
        token = pyotp.TOTP(secret).now()
        assert pyotp.TOTP(secret).verify(token, valid_window=1) is True

    def test_invalid_token_fails(self):
        import pyotp

        secret = pyotp.random_base32()
        assert pyotp.TOTP(secret).verify("000000") is False
