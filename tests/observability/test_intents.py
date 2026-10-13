from apiforge.observability.intents import diff_intent, make_intent


def test_intent_diff_is_stable() -> None:
    intent = make_intent("monitor", "orders", "errors", {"query": "errors"})
    assert diff_intent(intent, None).action == "create"
    assert diff_intent(intent, {"query": "errors"}).action == "unchanged"
