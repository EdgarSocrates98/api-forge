from apiforge.observability.instrumentation import recommend


def test_instrumentation_supports_target_languages() -> None:
    assert recommend("python", "fastapi")["standard"] == "opentelemetry"
    assert "otel" in str(recommend("go")["package"])
