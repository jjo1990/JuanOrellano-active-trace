import logging

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

logger = logging.getLogger(__name__)


def setup_otel(
    service_name: str = "activia-trace",
    otlp_endpoint: str | None = None,
) -> None:
    try:
        provider = TracerProvider()
        if otlp_endpoint:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
                OTLPSpanExporter,
            )
            exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            provider.add_span_processor(SimpleSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        logger.info("opentelemetry initialized", extra={"otlp_endpoint": otlp_endpoint})
    except Exception as exc:
        logger.warning("opentelemetry init skipped", extra={"error": str(exc)})


def instrument_fastapi(app: FastAPI) -> None:
    try:
        FastAPIInstrumentor.instrument_app(app)
    except Exception as exc:
        logger.warning("opentelemetry instrumentation skipped", extra={"error": str(exc)})
