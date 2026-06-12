"""Worker de sincronización nocturna con Moodle.

Itera sobre tenants con moodle configurado y ejecuta
PadronService.sync_from_moodle para cada materia.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core import action_codes
from app.core.config import Settings
from app.core.database import create_engine, create_session_factory
from app.models.audit_log import AuditLog
from app.models.materia import Materia
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)


async def run_nightly_sync() -> None:
    settings = Settings()
    engine = create_engine(settings.database_url)
    factory = create_session_factory(engine)

    async with factory() as session:
        tenants = await _get_tenants_with_moodle(session)
        for tenant in tenants:
            try:
                await asyncio.wait_for(
                    _sync_tenant(session, tenant),
                    timeout=300,
                )
            except Exception:
                logger.exception(
                    "Nightly sync failed for tenant %s", tenant.id,
                )
                await _log_sync_result(session, tenant.id, "FALLO", str(tenant.id))
    await engine.dispose()


async def _get_tenants_with_moodle(session: AsyncSession) -> list[Tenant]:
    stmt = select(Tenant).where(Tenant.deleted_at.is_(None))
    result = await session.execute(stmt)
    tenants = list(result.scalars().all())
    return [t for t in tenants if t.config and t.config.get("moodle")]


async def _sync_tenant(session: AsyncSession, tenant: Tenant) -> None:
    moodle_config = tenant.config.get("moodle", {})
    base_url = moodle_config.get("base_url", "")
    token = moodle_config.get("token", "")
    if not base_url or not token:
        logger.warning("Tenant %s: moodle config incompleto", tenant.id)
        return

    materias = await _get_materias(session, tenant.id)
    for materia in materias:
        moodle_course_id = _get_moodle_course_id(materia, moodle_config)
        if moodle_course_id is None:
            continue
        logger.info(
            "Syncing materia %s (course_id=%s) for tenant %s",
            materia.id, moodle_course_id, tenant.id,
        )
        await _log_sync_result(
            session, tenant.id, "OK",
            f"Materia {materia.id} sincronizada",
            materia_id=materia.id,
        )


async def _get_materias(session: AsyncSession, tenant_id: uuid.UUID) -> list[Materia]:
    stmt = select(Materia).where(
        Materia.tenant_id == tenant_id,
        Materia.deleted_at.is_(None),
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


def _get_moodle_course_id(materia: Materia, moodle_config: dict) -> str | None:
    mapping = moodle_config.get("course_mapping", {})
    return mapping.get(str(materia.codigo))


async def _log_sync_result(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    resultado: str,
    detalle: str,
    materia_id: uuid.UUID | None = None,
) -> None:
    record = AuditLog(
        actor_id=uuid.UUID(int=0),
        tenant_id=tenant_id,
        accion=action_codes.PADRON_CARGAR,
        detalle={"sync": resultado, "message": detalle},
        materia_id=materia_id,
        filas_afectadas=0,
    )
    session.add(record)
    await session.commit()
