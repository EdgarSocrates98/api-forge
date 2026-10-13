import pytest

from apiforge.observability.http_requester import host_http_requester


def test_host_requester_delegates_only_allowlisted_https() -> None:
    calls: list[tuple[str, str]] = []

    def fake_get(endpoint: str, params: dict[str, str], reference: str) -> dict[str, object]:
        calls.append((endpoint, reference))
        return {"data": [{"id": "trace-1"}]}

    requester = host_http_requester({"api.datadoghq.com"}, fake_get)

    response = requester.get("https://api.datadoghq.com/api/v2/apm/traces", {}, "broker:dd")

    assert response["data"] == [{"id": "trace-1"}]
    assert calls == [("https://api.datadoghq.com/api/v2/apm/traces", "broker:dd")]


@pytest.mark.parametrize(
    "endpoint",
    [
        "http://api.datadoghq.com/api/v2/apm/traces",
        "https://evil.example/api/v2/apm/traces",
        "https://{environment-id}.live.dynatrace.com/api/v2/metrics/query",
    ],
)
def test_host_requester_rejects_unsafe_or_unresolved_endpoints(endpoint: str) -> None:
    requester = host_http_requester({"api.datadoghq.com"}, lambda *_args: {})

    with pytest.raises(ValueError, match="AF-OBS-HTTP"):
        requester.get(endpoint, {}, "broker:provider")
