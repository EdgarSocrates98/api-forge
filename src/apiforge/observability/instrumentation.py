"""Framework-neutral instrumentation recommendations."""


def recommend(language: str, framework: str | None = None) -> dict[str, object]:
    normalized = language.lower()
    package = {
        "python": "opentelemetry-instrumentation",
        "go": "go.opentelemetry.io/otel",
        "java": "io.opentelemetry",
    }.get(normalized, "OpenTelemetry SDK")
    return {
        "language": normalized,
        "framework": framework,
        "standard": "opentelemetry",
        "package": package,
        "required_attributes": ("service.name", "deployment.environment", "http.route"),
    }
