from apiforge.observability.registry import capabilities


def test_vendor_capabilities_are_explicit() -> None:
    result = capabilities()
    assert set(result) == {"datadog", "dynatrace"}
    assert any(item["name"] == "apply" and item["supported"] is False for item in result["datadog"])
