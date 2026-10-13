from apiforge.observability.drift import compare
from apiforge.observability.intents import make_intent


def test_drift_is_explicit() -> None:
    intent = make_intent("monitor", "orders", "errors", {})
    assert compare((intent,), {})[0].action == "create"
