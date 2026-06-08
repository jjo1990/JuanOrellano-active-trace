"""Resolución y aislamiento de tenant.

Re-exporta modelos y mixin desde app.models para mantener
compatibilidad con imports existentes.
"""

from app.models.mixins import BaseModelMixin
from app.models.tenant import Tenant

__all__ = ["BaseModelMixin", "Tenant"]
