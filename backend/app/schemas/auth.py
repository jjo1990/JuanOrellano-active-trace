import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class Login2faRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    challenge_token: str
    totp_code: str


class ChallengeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    requires_2fa: bool = True
    challenge_token: str


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    refresh_token: str


class RefreshResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LogoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    refresh_token: str


class ForgotRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr


class ResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str
    new_password: str = Field(min_length=8)


class TwoFactorEnrollResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    secret: str
    uri: str


class TwoFactorVerifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    totp_code: str


class TwoFactorStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool


class UserInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    nombre: str
    apellidos: str

    @property
    def display_name(self) -> str:
        return f"{self.nombre} {self.apellidos}"
