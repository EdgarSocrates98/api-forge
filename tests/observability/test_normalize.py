from apiforge.observability.normalize import normalize_records


def test_normalizes_otel_like_records() -> None:
    records = normalize_records(({"id": "x", "kind": "span", "service": "orders", "http.route": "/orders/abcdef12", "status_code": 200},))
    assert records[0].operation == "/orders/:id"
    assert records[0].source_hash
