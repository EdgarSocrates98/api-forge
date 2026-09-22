"""Provider-neutral desired state and stable diffs."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import cast

from apiforge.contracts.observability import IntentDiff, IntentKind, Risk, VendorIntent
from apiforge.core.models import JsonValue


def intent_id(kind: str, service: str, name: str) -> str:
    return f"intent:{hashlib.sha256(f'{kind}:{service}:{name}'.encode()).hexdigest()[:16]}"


def make_intent(
    kind: str, service: str, name: str, specification: Mapping[str, object], risk: str = "read_only"
) -> VendorIntent:
    return VendorIntent(
        id=intent_id(kind, service, name),
        kind=cast(IntentKind, kind),
        service=service,
        name=name,
        specification=cast(Mapping[str, JsonValue], specification),
        risk=cast(Risk, risk),
        requires_approval=risk == "external_mutation",
    )


def diff_intent(desired: VendorIntent, observed: Mapping[str, object] | None) -> IntentDiff:
    if observed is None:
        return IntentDiff(
            intent_id=desired.id,
            action="create",
            changes=("resource absent",),
            risk=desired.risk,
            requires_approval=desired.requires_approval,
        )
    left = json.dumps(dict(desired.specification), sort_keys=True)
    right = json.dumps(dict(observed), sort_keys=True)
    if left == right:
        return IntentDiff(
            intent_id=desired.id,
            action="unchanged",
            risk=desired.risk,
            requires_approval=desired.requires_approval,
        )
    return IntentDiff(
        intent_id=desired.id,
        action="update",
        changes=("specification differs",),
        risk=desired.risk,
        requires_approval=desired.requires_approval,
    )
