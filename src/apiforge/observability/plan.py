"""Small deterministic plan builder."""

from apiforge.contracts.observability import VendorIntent
from apiforge.observability.governance import govern


def plan(
    intents: tuple[VendorIntent, ...], approved: bool = False, dry_run: bool = True
) -> list[dict[str, object]]:
    return [
        govern(intent, approved=approved, dry_run=dry_run).model_dump(mode="json")
        for intent in intents
    ]
