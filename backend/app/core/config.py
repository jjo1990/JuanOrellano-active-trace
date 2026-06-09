from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    database_url: str
    secret_key: str = Field(min_length=32)
    encryption_key: str = Field(min_length=32, max_length=32)
    access_token_expire_minutes: int = Field(default=15, ge=1)
    refresh_token_expire_days: int = Field(default=7, ge=1)
    jwt_algorithm: str = Field(default="HS256")
    totp_issuer: str = Field(default="activia-trace")
    otel_service_name: str = "activia-trace"
    otel_exporter_otlp_endpoint: str | None = None

    @field_validator("encryption_key")
    @classmethod
    def validate_encryption_key_length(cls, v: str) -> str:
        if len(v) != 32:
            msg = "ENCRYPTION_KEY must be exactly 32 characters"
            raise ValueError(msg)
        return v
