"""§29 knowledge drift detection — pack declaration vs observation receipts.

Zero receipts resolve to ``unresolved``; one receipt delegates to the
single-observation freshness check; two or more receipts that disagree on
source hash, source version or verdict resolve to ``conflicted`` with the
disagreeing pairs named. Nothing here fetches or rewrites knowledge.
"""

from __future__ import annotations

from apiforge.contracts.knowledge import (
    FreshnessResult,
    FreshnessState,
    KnowledgeDrift,
    SourceObservation,
)
from apiforge.knowledge.freshness import verify_pack_freshness
from apiforge.knowledge.loader import Pack


def _receipt_id(observation: SourceObservation) -> str:
    return f"{observation.source}@{observation.observed_at}"


def _conflict_pairs(
    receipts: tuple[tuple[SourceObservation, FreshnessResult], ...],
) -> tuple[str, ...]:
    conflicts: list[str] = []
    for index, left in enumerate(receipts):
        for right in receipts[index + 1 :]:
            left_obs, left_result = left
            right_obs, right_result = right
            reasons: list[str] = []
            if (
                left_obs.source_hash
                and right_obs.source_hash
                and left_obs.source_hash != right_obs.source_hash
            ):
                reasons.append("source_hash differs between receipts")
            if (
                left_obs.source_version
                and right_obs.source_version
                and left_obs.source_version != right_obs.source_version
            ):
                reasons.append(
                    f"source_version {left_obs.source_version!r} != {right_obs.source_version!r}"
                )
            if left_result.state != right_result.state:
                reasons.append(f"freshness verdict {left_result.state} != {right_result.state}")
            if reasons:
                conflicts.append(
                    f"{_receipt_id(left_obs)} vs {_receipt_id(right_obs)}: " + "; ".join(reasons)
                )
    return tuple(conflicts)


def detect_pack_drift(
    pack: Pack,
    observations: tuple[SourceObservation, ...],
    *,
    now: str,
) -> KnowledgeDrift:
    """Roll up one or more read-only receipts into a drift verdict."""
    signals: list[str] = []
    unresolved: list[str] = []
    if not observations:
        return KnowledgeDrift(
            domain=pack.domain,
            pack_version=pack.version,
            state="unresolved",
            signals=("no observation receipts supplied",),
            unresolved=("no read-only source observation receipt is available",),
            observations=0,
        )
    receipts = tuple(
        (observation, verify_pack_freshness(pack, observation, now=now))
        for observation in observations
    )
    states = {result.state for _, result in receipts}
    conflicts = _conflict_pairs(receipts)
    if conflicts or len(states) > 1:
        state: FreshnessState = "conflicted"
        signals.append("receipts disagree — human reconciliation required")
    else:
        state = receipts[0][1].state
        signals.append(f"all {len(receipts)} receipt(s) agree: {state}")
    for _, result in receipts:
        if result.state == "unresolved":
            unresolved.append(f"{result.source}: {result.reason}")
    return KnowledgeDrift(
        domain=pack.domain,
        pack_version=pack.version,
        state=state,
        signals=tuple(signals),
        conflicts=conflicts,
        unresolved=tuple(unresolved),
        observations=len(receipts),
        evidence=receipts[0][1].evidence,
    )
