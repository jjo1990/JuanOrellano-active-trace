"""Global exception handlers para errores de dominio conocidos.

Cada handler traduce una excepción de negocio a una respuesta HTTP
estructurada con FastAPI, manteniendo el detalle del error legible
sin exponer información sensible.
"""

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AuthError,
    ChallengeExpiredError,
    InvalidCredentialsError,
    RateLimitExceededError,
    RepositoryError,
    TenantNotFoundError,
    TokenExpiredError,
    TokenInvalidError,
    TwoFactorInvalidError,
    TwoFactorRequiredError,
)


async def _auth_error_handler(request: Request, exc: AuthError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


async def _rate_limit_handler(request: Request, exc: RateLimitExceededError) -> JSONResponse:
    return JSONResponse(status_code=429, content={"detail": str(exc)})


async def _tenant_not_found_handler(request: Request, exc: TenantNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def _repository_error_handler(request: Request, exc: RepositoryError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


# Mapa de handlers registrables en el ciclo de vida de la app
HANDLERS: list[tuple[type[Exception], type]] = [
    (InvalidCredentialsError, _auth_error_handler),
    (TokenExpiredError, _auth_error_handler),
    (TokenInvalidError, _auth_error_handler),
    (ChallengeExpiredError, _auth_error_handler),
    (TwoFactorRequiredError, _auth_error_handler),
    (TwoFactorInvalidError, _auth_error_handler),
    (RateLimitExceededError, _rate_limit_handler),
    (TenantNotFoundError, _tenant_not_found_handler),
    (RepositoryError, _repository_error_handler),
]
