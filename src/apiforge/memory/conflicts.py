"""Deterministic contradiction detection for applicable memory records."""

from __future__ import annotations

import hashlib
import json
from itertools import combinations

from apiforge.contracts.agentic_memory import MemoryConflict, MemoryQuery, MemoryRecord
from apiforge.memory.matching import effective_freshness, runtime_match

_TRUST = {"unknown": 0, "candidate": 1, "untrusted": 1, "observed": 2, "trusted": 3, "verified": 4}
_AUTHORITY = {
    "unknown": 0.0,
    "model_generated": 0.0,
    "external_untrusted": 0.0,
    "external_data": 0.25,
    "tool_result": 0.25,
    "user_data": 0.25,
    "memory": 0.5,
    "knowledge": 0.75,
    "trusted_internal": 0.75,
    "verified_evidence": 1.0,
    "governed_policy": 1.0,
    "system": 1.0,
}


def _scalar_paths(value: object, prefix: str = "") -> dict[str, object]:
    if isinstance(value, dict):
        result: dict[str, object] = {}
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            result.update(_scalar_paths(child, path))
        return result
    if isinstance(value, list):
        return {}
    return {prefix: value}


def _applicable(left: MemoryRecord, right: MemoryRecord, query: MemoryQuery) -> bool:
    if (
        left.environment_fingerprint
        and right.environment_fingerprint
        and left.environment_fingerprint != right.environment_fingerprint
    ):
        return False
    for key in set(left.applicability) & set(right.applicability):
        if left.applicability[key] != right.applicability[key]:
            return False
    if query.runtime:
        left_ok, _, _ = runtime_match(left, query.runtime)
        right_ok, _, _ = runtime_match(right, query.runtime)
        return left_ok and right_ok
    return True


def _digest(left: str, right: str, paths: tuple[str, ...]) -> str:
    encoded = json.dumps([left, right, paths], separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


def _score(record: MemoryRecord, query: MemoryQuery) -> tuple[float, dict[str, float]]:
    trust = _TRUST[record.trust_level] / 4.0
    evidence = min(1.0, len(record.evidence_refs) / 2.0)
    outcome = 1.0 if record.outcome in {"persisted", "reinforced"} else 0.5
    _, runtime, _ = runtime_match(record, query.runtime)
    policy = 1.0 if query.policy_version and record.policy_version == query.policy_version else 0.5
    authority = _AUTHORITY[record.origin]
    signals = {
        "freshness": 1.0,
        "trust": trust,
        "evidence_depth": evidence,
        "outcome_success": outcome,
        "runtime_compatibility": runtime,
        "policy_version": policy,
        "source_authority": authority,
    }
    return (
        0.25 * trust
        + 0.2 * evidence
        + 0.15 * outcome
        + 0.1 * runtime
        + 0.1 * policy
        + 0.2 * authority,
        signals,
    )


def detect_memory_conflicts(
    records: tuple[MemoryRecord, ...] | list[MemoryRecord], query: MemoryQuery
) -> tuple[MemoryConflict, ...]:
    """Return only fresh, trusted, applicable contradictions."""
    candidates = [
        record
        for record in records
        if _TRUST[record.trust_level] >= _TRUST["observed"]
        and effective_freshness(record, query.now) == "fresh"
    ]
    conflicts: list[MemoryConflict] = []
    for left, right in combinations(sorted(candidates, key=lambda item: item.memory_id), 2):
        if not _applicable(left, right, query):
            continue
        left_paths = _scalar_paths(left.payload)
        right_paths = _scalar_paths(right.payload)
        paths = tuple(
            sorted(
                path
                for path in set(left_paths) & set(right_paths)
                if left_paths[path] != right_paths[path]
            )
        )
        if not paths:
            continue
        left_score, left_signals = _score(left, query)
        right_score, right_signals = _score(right, query)
        preferred_id: str | None = None
        conflicting_id: str | None = None
        # Destructive risk quarantines before scoring is consulted: prefer_*
        # is an advisory preference, never an authorization to destroy.
        if query.risk == "destructive":
            outcome = "quarantine"
            admission_effect: str = "exclude_both"
            unresolved: tuple[str, ...] = ("destructive action requires conflict quarantine",)
        elif abs(left_score - right_score) >= 0.15:
            outcome = "prefer_a" if left_score > right_score else "prefer_b"
            admission_effect = "admit_preferred"
            preferred_id = left.memory_id if left_score > right_score else right.memory_id
            conflicting_id = right.memory_id if left_score > right_score else left.memory_id
            unresolved = ()
        else:
            outcome = "review"
            admission_effect = "review_only"
            unresolved = ("conflicting applicable memory requires review",)
        signals = {f"a_{key}": value for key, value in left_signals.items()} | {
            f"b_{key}": value for key, value in right_signals.items()
        }
        conflict_id = "memory-conflict:" + _digest(left.memory_id, right.memory_id, paths)
        conflicts.append(
            MemoryConflict(
                conflict_id=conflict_id,
                memory_a_id=left.memory_id,
                memory_b_id=right.memory_id,
                outcome=outcome,  # type: ignore[arg-type]
                conflicting_paths=paths,
                signals=signals,
                preferred_memory_id=preferred_id,
                conflicting_memory_id=conflicting_id,
                admission_effect=admission_effect,  # type: ignore[arg-type]
                reason=f"applicable records disagree at {', '.join(paths)}",
                unresolved=unresolved,
            )
        )
    return tuple(conflicts)


__all__ = ["detect_memory_conflicts"]
