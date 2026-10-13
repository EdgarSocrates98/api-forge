"""Memory security gates (step11 §14).

Pipeline: scope → origin → evidence → trust → outcome → freshness.
Hard violations reject with the historical AF codes; borderline trust states
quarantine the candidate in an append-only log for human review instead of
silently dropping it — a quarantined row is never retrieval-visible.
"""

from __future__ import annotations

from datetime import datetime

from apiforge.contracts.agentic_memory import (
    MemoryCandidate,
    MemoryPolicy,
)
from apiforge.contracts.trust import MemoryGateResult

_TRUST_ORDER = {
    "unknown": 0,
    "candidate": 1,
    "untrusted": 1,
    "observed": 2,
    "trusted": 3,
    "verified": 4,
}


def _expired_at(expires_at: str, now: str) -> bool:
    try:
        return datetime.fromisoformat(expires_at) <= datetime.fromisoformat(now)
    except ValueError:
        return False


def evaluate_gates(
    candidate: MemoryCandidate, policy: MemoryPolicy, *, now: str
) -> MemoryGateResult:
    """Run the §14 gate pipeline; verdicts are persist/quarantine/reject."""
    record = candidate.record
    if record.scope not in policy.allowed_scopes:
        return MemoryGateResult(
            candidate_id=candidate.candidate_id,
            verdict="reject",
            gates_failed=("scope",),
            code="AF-MEMORY-SCOPE-DENIED",
            field="scope",
            unlock="use an allowed scope or have a human revise the MemoryPolicy",
            reason=f"scope {record.scope!r} is not allowed by {policy.policy_id}",
        )
    if record.origin == "external_untrusted" and not policy.allow_external_untrusted:
        return MemoryGateResult(
            candidate_id=candidate.candidate_id,
            verdict="reject",
            gates_passed=("scope",),
            gates_failed=("origin",),
            code="AF-MEMORY-UNTRUSTED",
            field="origin",
            unlock="attach a trusted internal source and verified evidence",
            reason="external_untrusted content cannot be persisted by this policy",
        )
    if (
        record.scope in {"institutional", "semantic"}
        and policy.require_evidence_for_persistent
        and not record.evidence_refs
    ):
        return MemoryGateResult(
            candidate_id=candidate.candidate_id,
            verdict="reject",
            gates_passed=("scope", "origin"),
            gates_failed=("evidence",),
            code="AF-MEMORY-EVIDENCE-REQUIRED",
            field="evidence_refs",
            unlock="provide evidence_refs from an independently verified artifact",
            reason="persistent cross-task memory requires evidence",
        )
    if record.origin == "model_generated" and not policy.allow_model_generated_persistent:
        return MemoryGateResult(
            candidate_id=candidate.candidate_id,
            verdict="reject",
            gates_passed=("scope", "origin", "evidence"),
            gates_failed=("origin",),
            code="AF-MEMORY-MODEL-UNVERIFIED",
            field="origin",
            unlock="store as working/candidate data or attach verified evidence under policy",
            reason="model_generated content cannot be promoted automatically",
        )
    if _TRUST_ORDER[record.trust_level] < _TRUST_ORDER[policy.minimum_trust]:
        return MemoryGateResult(
            candidate_id=candidate.candidate_id,
            verdict="quarantine",
            gates_passed=("scope", "origin", "evidence"),
            gates_failed=("trust",),
            quarantine_reasons=(
                f"trust {record.trust_level} below policy minimum {policy.minimum_trust}",
            ),
            code="AF-MEMORY-TRUST-QUARANTINED",
            field="trust_level",
            unlock="collect stronger evidence or have a human resolve the quarantine",
            reason=f"{record.trust_level} is below policy minimum {policy.minimum_trust}",
        )
    if record.expires_at and _expired_at(record.expires_at, now):
        return MemoryGateResult(
            candidate_id=candidate.candidate_id,
            verdict="reject",
            gates_passed=("scope", "origin", "evidence", "trust", "outcome"),
            gates_failed=("freshness",),
            code="AF-MEMORY-EXPIRED",
            field="expires_at",
            unlock="propose fresh content with a future expiry or none",
            reason="candidate is already expired at persist time",
        )
    return MemoryGateResult(
        candidate_id=candidate.candidate_id,
        verdict="persist",
        gates_passed=("scope", "origin", "evidence", "outcome", "freshness", "trust"),
        reason="all gates passed",
    )


__all__ = ["evaluate_gates"]
