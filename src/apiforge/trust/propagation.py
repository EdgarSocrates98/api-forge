"""Deterministic taint propagation across transforms (step11 §10).

Rules:

* taint is the union of source taints — transforms never silently clean data;
* only a ``governed_verification`` transform backed by ``evidence_refs`` may
  drop ``external``/``unverified_source``/``untrusted`` taints and lift the
  derived trust level to at most ``verified``;
* ``instruction_authority`` never widens: any ``none`` source forces ``none``,
  and only ``system_synthesis`` over fully authoritative inputs may keep it.
"""

from __future__ import annotations

from apiforge.contracts.agentic_memory import TrustLevel
from apiforge.contracts.trust import (
    PropagationTransform,
    TrustBoundary,
    TrustPropagation,
    TrustUnit,
)

#: Deterministic trust ranking shared by propagation and context admission.
TRUST_ORDER: dict[TrustLevel, int] = {
    "unknown": 0,
    "untrusted": 1,
    "candidate": 1,
    "observed": 2,
    "trusted": 3,
    "verified": 4,
}
_TRUST_ORDER = TRUST_ORDER
_AUTHORITY_ORDER = {"none": 0, "policy": 1, "system": 2}
_LEVEL_BY_ORDER: dict[int, TrustLevel] = {
    0: "unknown",
    1: "candidate",
    2: "observed",
    3: "trusted",
    4: "verified",
}
#: Taints a governed verification with evidence can clear.
_REMOVABLE_TAINT = frozenset({"external", "unverified_source", "untrusted", "tool_output"})


def propagate(
    sources: tuple[TrustUnit, ...],
    *,
    transform: PropagationTransform,
    subject: str,
    boundary: TrustBoundary | None = None,
    scope: str = "",
    provenance: tuple[str, ...] = (),
    evidence_refs: tuple[str, ...] = (),
    reason: str = "",
) -> TrustPropagation:
    """Derive one TrustUnit from sources under an explicit transform."""
    if not sources:
        raise ValueError("AF-TRUST-PROPAGATION-EMPTY: propagation requires at least one source")
    taint = sorted({mark for unit in sources for mark in unit.taint})
    weakest_unit = min(sources, key=lambda u: (_TRUST_ORDER[u.trust_level], u.subject))
    weakest = _TRUST_ORDER[weakest_unit.trust_level]
    # preserve the weakest level's exact label: "untrusted" must not silently
    # widen into "candidate" just because they share an order bucket
    derived_level = weakest_unit.trust_level
    taint_reduced = False
    if transform == "governed_verification" and evidence_refs:
        kept = [mark for mark in taint if mark not in _REMOVABLE_TAINT]
        taint_reduced = len(kept) != len(taint)
        taint = kept
        # Verified evidence may lift the claim, never above "verified" and only
        # one tier above the weakest source: a parser cannot manufacture trust.
        derived_level = _LEVEL_BY_ORDER[min(weakest + 1, 4)]
    authorities = {unit.instruction_authority for unit in sources}
    if transform == "system_synthesis" and "none" not in authorities:
        authority = min(authorities, key=lambda a: _AUTHORITY_ORDER[a])
    else:
        authority = "none"
    derived = TrustUnit(
        subject=subject,
        boundary=boundary or weakest_unit.boundary,
        origin=weakest_unit.origin,
        trust_level=derived_level,
        taint=tuple(taint),
        instruction_authority=authority,
        scope=scope or weakest_unit.scope,
        provenance=tuple(provenance) + tuple(mark for unit in sources for mark in unit.provenance),
        freshness=weakest_unit.freshness,
        evidence_refs=tuple(evidence_refs),
    )
    return TrustPropagation(
        transform=transform,
        derived=derived,
        derived_from=tuple(unit.subject for unit in sources),
        taint_reduced=taint_reduced,
        reason=reason,
    )


__all__ = ["TRUST_ORDER", "propagate"]
