"""Worker entrypoint — placeholder.

Real queue technology (asyncio / Celery / ARQ) will be decided in ADR-003.
"""
import asyncio
import logging

from app.core.logging import setup_logging

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logging()
    logger.info("worker started — placeholder, no-op loop")
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("worker stopped")


if __name__ == "__main__":
    asyncio.run(main())
