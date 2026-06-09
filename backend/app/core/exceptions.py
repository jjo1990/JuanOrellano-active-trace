class TenantNotFoundError(Exception):
    """El tenant no existe o está inactivo."""


class EncryptionError(Exception):
    """Fallo en operación de cifrado/descifrado."""


class RepositoryError(Exception):
    """Error genérico de repositorio (permiso, consistencia, etc.)."""


class AuthError(Exception):
    """Error genérico de autenticación."""


class InvalidCredentialsError(AuthError):
    """Credenciales inválidas (email o password incorrectos)."""


class TokenExpiredError(AuthError):
    """Token JWT expirado."""


class TokenInvalidError(AuthError):
    """Token JWT inválido (firma, formato o claims)."""


class ChallengeExpiredError(AuthError):
    """Challenge token de 2FA expirado."""


class TwoFactorRequiredError(AuthError):
    """2FA requerido para completar login."""


class TwoFactorInvalidError(AuthError):
    """Código TOTP inválido."""


class RateLimitExceededError(AuthError):
    """Demasiados intentos de login."""
