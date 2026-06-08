"""RED → GREEN → TRIANGULATE: Configuración tipada.

Task 2.x — Strict TDD.
"""
import pytest
from pydantic import ValidationError


class TestSettingsValidEnv:
    def test_loads_with_all_required_vars(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/db")
        monkeypatch.setenv("SECRET_KEY", "x" * 32)
        monkeypatch.setenv("ENCRYPTION_KEY", "y" * 32)
        monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)

        from app.core.config import Settings

        settings = Settings(_env_file=None)
        assert settings.database_url == "postgresql+asyncpg://u:p@localhost:5432/db"
        assert settings.secret_key == "x" * 32
        assert settings.encryption_key == "y" * 32
        assert settings.access_token_expire_minutes == 15

    def test_default_access_token_expire(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/db")
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)
        monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)

        from app.core.config import Settings

        settings = Settings(_env_file=None)
        assert settings.access_token_expire_minutes == 15

    def test_custom_access_token_expire(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/db")
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)
        monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

        from app.core.config import Settings

        settings = Settings(_env_file=None)
        assert settings.access_token_expire_minutes == 30


class TestSettingsMissingVar:
    def test_missing_database_url_fails(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)

        from app.core.config import Settings

        with pytest.raises(ValidationError):
            Settings(_env_file=None)

    def test_short_secret_key_fails(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/db")
        monkeypatch.setenv("SECRET_KEY", "short")
        monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)

        from app.core.config import Settings

        with pytest.raises(ValidationError):
            Settings(_env_file=None)

    def test_wrong_length_encryption_key_fails(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/db")
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        monkeypatch.setenv("ENCRYPTION_KEY", "wrong_length")

        from app.core.config import Settings

        with pytest.raises(ValidationError):
            Settings(_env_file=None)


class TestSettingsInvalidType:
    def test_access_token_not_int_fails(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/db")
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        monkeypatch.setenv("ENCRYPTION_KEY", "b" * 32)
        monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "not_a_number")

        from app.core.config import Settings

        with pytest.raises(ValidationError):
            Settings(_env_file=None)
