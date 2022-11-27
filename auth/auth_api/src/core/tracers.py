from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.sdk.resources import Resource

from src.core.config import jaeger_settings


def configure_tracer() -> None:
    sampler = TraceIdRatioBased(jaeger_settings.sampling_ratio)
    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({
                "service.name": jaeger_settings.auth_project_name,
            }),
            sampler=sampler
        )
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=jaeger_settings.agent_host,
                agent_port=jaeger_settings.agent_port,
            )
        )
    )
