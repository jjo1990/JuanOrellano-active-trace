from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routers.health import router as health_router
from app.core.config import Settings
from app.core.database import create_engine, create_session_factory
from app.core.logging import setup_logging
from app.core.observability import instrument_fastapi, setup_otel


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = Settings()
    setup_logging()
    setup_otel(
        service_name=settings.otel_service_name,
        otlp_endpoint=settings.otel_exporter_otlp_endpoint,
    )
    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)
    app.state.engine = engine
    app.state.session_factory = session_factory
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="activia-trace", version="0.1.0", lifespan=lifespan)
    app.include_router(health_router)
    instrument_fastapi(app)
    return app


app = create_app()
