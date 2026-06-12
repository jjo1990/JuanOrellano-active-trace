"""Worker asincrónico de despacho de comunicaciones (C-12).

Consume comunicaciones Pendiente, las transiciona a Enviando,
ejecuta _send_email (mockeado para MVP) y las marca Enviado o Error.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.core.database import create_engine, create_session_factory
from app.models.comunicacion import Comunicacion
from app.repositories.comunicacion_repository import ComunicacionRepository
from app.services.comunicacion_service import validate_transition

logger = logging.getLogger(__name__)


def _send_email(destinatario: str, asunto: str, cuerpo: str) -> bool:
    logger.info(
        "EMAIL_SIMULATED",
        extra={
            "to": destinatario,
            "subject": asunto,
            "body_length": len(cuerpo),
        },
    )
    return True


async def _process_one(db: AsyncSession, com: Comunicacion) -> None:
    validate_transition(com.estado, "Enviando")
    com.estado = "Enviando"
    await db.commit()

    _send_email(com.destinatario or "", com.asunto, com.cuerpo)

    validate_transition("Enviando", "Enviado")
    com.estado = "Enviado"
    com.enviado_at = datetime.now(timezone.utc)


async def run_worker(
    session_factory: async_sessionmaker[AsyncSession],
    tenant_id: uuid.UUID,
    poll_interval: int = 5,
    batch_size: int = 10,
) -> None:
    logger.info(
        "Dispatch worker started — tenant=%s poll=%ds batch=%d",
        tenant_id, poll_interval, batch_size,
    )

    while True:
        try:
            async with session_factory() as db:
                repo = ComunicacionRepository(db, tenant_id)
                pendientes = await repo.get_pendientes(limit=batch_size)

                for com in pendientes:
                    try:
                        await _process_one(db, com)
                    except ValueError:
                        logger.error(
                            "Transición inválida para comunicación %s (estado=%s)",
                            com.id, com.estado,
                        )
                    except Exception:
                        logger.exception(
                            "Error despachando comunicación %s", com.id,
                        )
                        try:
                            com.estado = "Error"
                        except Exception:
                            logger.exception(
                                "No se pudo marcar Error en comunicación %s", com.id,
                            )
                    await db.commit()

        except Exception:
            logger.exception("Error en ciclo del worker — reintentando en %ds", poll_interval)

        await asyncio.sleep(poll_interval)


if __name__ == "__main__":
    settings = Settings()
    engine = create_engine(settings.database_url)
    factory = create_session_factory(engine)
    asyncio.run(run_worker(factory, uuid.UUID(int=0)))
