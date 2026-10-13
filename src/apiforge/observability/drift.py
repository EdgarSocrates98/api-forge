"""Observed/desired state comparison."""

from collections.abc import Mapping

from apiforge.contracts.observability import IntentDiff, VendorIntent
from apiforge.observability.intents import diff_intent


def compare(
    desired: tuple[VendorIntent, ...], observed: Mapping[str, Mapping[str, object]]
) -> tuple[IntentDiff, ...]:
    return tuple(diff_intent(item, observed.get(item.id)) for item in desired)
