class TenantNotFoundError(Exception):
    """El tenant no existe o está inactivo."""


class EncryptionError(Exception):
    """Fallo en operación de cifrado/descifrado."""


class RepositoryError(Exception):
    """Error genérico de repositorio (permiso, consistencia, etc.)."""
