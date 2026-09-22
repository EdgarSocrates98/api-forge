from apiforge.observability.query import build_provider_params
from apiforge.observability.read import build_read_plan


def test_datadog_query_uses_service_filter() -> None:
    params = build_provider_params(build_read_plan("datadog", "orders", "start", "end"))

    assert params["filter[query]"] == "service:orders"
    assert params["filter[from]"] == "start"


def test_dynatrace_query_is_encoded_without_credentials() -> None:
    plan = build_read_plan("dynatrace", "orders", "start", "end", environment="prod")

    params = build_provider_params(plan)

    assert params["entitySelector"].startswith("type(SERVICE)")
    assert "credential" not in " ".join(params).lower()


def test_cloudwatch_and_otel_queries_have_provider_shape() -> None:
    cloudwatch = build_provider_params(build_read_plan("cloudwatch", "orders", "start", "end"))
    otel = build_provider_params(build_read_plan("otel", "orders", "start", "end"))

    assert cloudwatch["Namespace"] == "orders"
    assert otel["service.name"] == "orders"
