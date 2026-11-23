"""OpenTelemetry setup. Exports via OTLP if configured, else to the console."""

import os

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def setup_tracing(service_name: str = "agent-eval") -> trace.Tracer:
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"):
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        exporter = OTLPSpanExporter()
    elif os.getenv("AGENT_EVAL_CONSOLE_TRACES"):
        exporter = ConsoleSpanExporter()
    else:
        exporter = None
    if exporter:
        provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return trace.get_tracer("agent_eval")


def traced_node(tracer: trace.Tracer, name: str, fn):
    """Wrap a LangGraph node so each invocation emits a span."""

    def wrapper(state):
        with tracer.start_as_current_span(f"node.{name}") as span:
            span.set_attribute("agent.node", name)
            return fn(state)

    return wrapper
