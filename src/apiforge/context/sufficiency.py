"""Minimum Sufficient Context: prune unused refs, re-measure, compare quality.

The deterministic fixpoint of the prompt's loop — start from the full
selection, drop refs that never reached a consumer and are not required,
re-evaluate the same metric catalog and keep the pruned set only when the
declared gate does not regress. ``strict`` keeps the pruned set only when no
required or evidence ref is lost and recall never drops; ``evidence`` allows
recall to be ``unresolved``; ``permissive`` reports the prune without gating.
"""

from __future__ import annotations

from collections.abc import Iterable

from apiforge.context.quality import evaluate, metric_map, used_uris
from apiforge.contracts.context import ContextRef
from apiforge.contracts.context_quality import (
    EVIDENCE_KINDS,
    ContextSufficiencyResult,
    ContextUseRecord,
    SufficiencyGate,
)

GATED_METRICS = ("context_recall", "evidence_recall")


def minimum_sufficient(
    refs: tuple[ContextRef, ...],
    uses: tuple[ContextUseRecord, ...],
    *,
    run_id: str,
    capsule_id: str | None = None,
    required_uris: Iterable[str] = (),
    gate: SufficiencyGate = "strict",
) -> ContextSufficiencyResult:
    """One deterministic pass to the fixpoint: keep consumed + required refs."""
    required = set(required_uris)
    consumed = used_uris(uses)
    by_uri = {ref.uri: ref for ref in refs}

    keep_uris = consumed | required
    if gate != "permissive":
        keep_uris |= {ref.uri for ref in refs if ref.kind in EVIDENCE_KINDS}
    kept = [ref.uri for ref in refs if ref.uri in keep_uris]
    pruned = [ref.uri for ref in refs if ref.uri not in keep_uris]
    pruned_bytes = sum(by_uri[uri].size_bytes for uri in pruned)

    unresolved: list[str] = []
    missing_required = sorted(required - set(by_uri))
    if missing_required:
        unresolved.append(f"required refs absent from selection: {missing_required}")

    before = evaluate(refs, uses, run_id=run_id, capsule_id=capsule_id, required_uris=required)
    kept_refs = tuple(ref for ref in refs if ref.uri in keep_uris)
    kept_uses = tuple(use for use in uses if use.ref_uri in keep_uris)
    after = evaluate(
        kept_refs, kept_uses, run_id=run_id, capsule_id=capsule_id, required_uris=required
    )

    sufficient = not missing_required
    before_map, after_map = metric_map(before.metrics), metric_map(after.metrics)
    for name in GATED_METRICS:
        first, second = before_map[name], after_map[name]
        veto = gate == "strict" or (gate == "evidence" and name == "evidence_recall")
        if second.basis == "unresolved":
            if first.basis == "observed" and veto:
                unresolved.append(f"{name} became unmeasurable after pruning")
                sufficient = False
            continue
        if first.basis == "observed" and (second.value or 0.0) < (first.value or 0.0):
            unresolved.append(f"{name} regressed: {first.value} -> {second.value}")
            if veto:
                sufficient = False
    if not pruned:
        unresolved.append("no unused or unrequired ref to prune; selection already minimal")

    return ContextSufficiencyResult(
        run_id=run_id,
        capsule_id=capsule_id,
        gate=gate,
        kept_refs=tuple(kept),
        pruned_refs=tuple(pruned),
        pruned_bytes=pruned_bytes,
        metrics_before=before.metrics,
        metrics_after=after.metrics,
        sufficient=sufficient,
        unresolved=tuple(sorted(set(unresolved))),
    )


__all__ = ["minimum_sufficient"]
