from apiforge.observability.governance import govern
from apiforge.observability.intents import make_intent


def test_external_mutation_requires_approval() -> None:
    intent = make_intent("monitor", "orders", "errors", {}, risk="external_mutation")
    assert govern(intent, dry_run=False).status == "refused"
    assert govern(intent, approved=True, dry_run=True).status == "dry_run"
