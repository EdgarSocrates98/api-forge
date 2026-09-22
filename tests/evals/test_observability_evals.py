from apiforge.observability.redaction import normalize_route


def test_observability_eval_route_normalization() -> None:
    assert normalize_route("/orders/12345678") == "/orders/:id"
