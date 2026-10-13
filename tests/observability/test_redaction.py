from apiforge.observability.redaction import normalize_route, redact_attributes


def test_secrets_are_redacted_and_ids_are_bounded() -> None:
    assert redact_attributes({"authorization": "secret", "tenant": "a"}) == {
        "authorization": "[REDACTED]",
        "tenant": "a",
    }
    assert normalize_route("/orders/abcdef12") == "/orders/:id"
