"""Append-only, evidence-gated memory persistence.

The store never executes provider code, calls a model or deletes a memory.
Invalidation is an event and retrieval reports stale/unresolved state instead
of silently treating it as fresh truth.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import cast

from apiforge.contracts.agentic_memory import (
    MemoryCandidate,
    MemoryInvalidation,
    MemoryOutcome,
    MemoryPolicy,
    MemoryQuery,
    MemoryRecord,
    MemoryRetrievalResult,
    MemoryTrust,
    TrustLevel,
)
from apiforge.contracts.trust import MemoryGateResult, MemoryQuarantine
from apiforge.core.io import sha256_file
from apiforge.core.models import JsonValue
from apiforge.memory.security import evaluate_gates

_MEMORY_DIR = Path(".apiforge") / "memory"
_RECORDS = "records.jsonl"
_CANDIDATES = "candidates.jsonl"
_INVALIDATIONS = "invalidations.jsonl"
_QUARANTINE = "quarantine.jsonl"
_TRUST_ORDER = {
    "unknown": 0,
    "candidate": 1,
    "untrusted": 1,
    "observed": 2,
    "trusted": 3,
    "verified": 4,
}


def _directory(root: Path) -> Path:
    resolved = Path(root).resolve()
    if resolved.name == ".apiforge":
        resolved = resolved.parent
    return resolved / _MEMORY_DIR


def _append(directory: Path, filename: str, payload: object) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    line = json.dumps(
        payload.model_dump(mode="json") if hasattr(payload, "model_dump") else payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(line + "\n")
    return path


def _read[ModelT](directory: Path, filename: str, model: type[ModelT]) -> list[ModelT]:
    path = directory / filename
    if not path.is_file():
        return []
    rows: list[ModelT] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(model.model_validate(json.loads(line)))  # type: ignore[attr-defined]
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(f"AF-MEMORY-STORE-CORRUPT: {path}:{line_no}: {exc}") from exc
    return rows


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    import hashlib

    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _refusal(code: str, field: str, unlock: str, detail: str) -> MemoryOutcome:
    return MemoryOutcome(
        action="rejected",
        accepted=False,
        code=code,
        field=field,
        unlock=unlock,
        reason=detail,
        unresolved=(code,),
    )


def propose_memory(
    root: Path,
    *,
    scope: str,
    origin: str,
    payload: object,
    proposed_by: str,
    reason: str,
    created_at: str,
    observed_at: str | None = None,
    expires_at: str | None = None,
    trust_level: str = "candidate",
    provenance: tuple[str, ...] = (),
    evidence_refs: tuple[str, ...] = (),
    environment_fingerprint: str | None = None,
    applicability: dict[str, object] | None = None,
    runtime_constraints: tuple[str, ...] = (),
) -> MemoryCandidate:
    """Observe a candidate; this step never makes it institutional truth."""
    normalized = MemoryRecord(
        memory_id="memory:"
        + _digest({"scope": scope, "payload": payload, "provenance": provenance})[:16],
        scope=scope,  # type: ignore[arg-type]
        origin=origin,  # type: ignore[arg-type]
        created_at=created_at,
        observed_at=observed_at,
        expires_at=expires_at,
        trust_level=trust_level,  # type: ignore[arg-type]
        provenance=provenance,
        evidence_refs=evidence_refs,
        environment_fingerprint=environment_fingerprint,
        applicability=cast(dict[str, JsonValue], applicability or {}),
        runtime_constraints=runtime_constraints,
        payload=payload,  # type: ignore[arg-type]
        trust=MemoryTrust(level=cast(TrustLevel, trust_level), evidence_refs=evidence_refs),
        content_sha256=_digest(payload),
    )
    candidate = MemoryCandidate(
        candidate_id="candidate:" + _digest(normalized.model_dump(mode="json"))[:16],
        record=normalized,
        proposed_by=proposed_by,
        reason=reason,
    )
    _append(_directory(root), _CANDIDATES, candidate)
    return candidate


def _quarantine_row(
    candidate: MemoryCandidate, gate: MemoryGateResult, now: str
) -> MemoryQuarantine:
    return MemoryQuarantine(
        quarantine_id="quarantine:" + _digest({"candidate": candidate.candidate_id})[:16],
        candidate_id=candidate.candidate_id,
        memory_id=candidate.record.memory_id,
        state="quarantined",
        reasons=gate.quarantine_reasons or (gate.reason,),
        created_at=now,
    )


def _quarantine_outcome(
    root: Path, candidate: MemoryCandidate, gate: MemoryGateResult, now: str
) -> MemoryOutcome:
    """Park the candidate in the append-only quarantine log (deduplicated)."""
    directory = _directory(root)
    row = _quarantine_row(candidate, gate, now)
    existing = _read(directory, _QUARANTINE, MemoryQuarantine)
    if not any(item.quarantine_id == row.quarantine_id for item in existing):
        _append(directory, _QUARANTINE, row)
    return MemoryOutcome(
        action="quarantined",
        memory_id=candidate.record.memory_id,
        accepted=False,
        code=gate.code,
        field=gate.field,
        unlock=gate.unlock,
        reason=gate.reason,
        evidence_refs=candidate.record.evidence_refs,
        unresolved=(gate.code,) if gate.code else (),
    )


def persist_candidate(
    root: Path, candidate: MemoryCandidate, policy: MemoryPolicy, *, now: str
) -> MemoryOutcome:
    """Run the §14 gate pipeline, then persist, quarantine or reject."""
    record = candidate.record
    gate = evaluate_gates(candidate, policy, now=now)
    if gate.verdict == "reject":
        return _refusal(
            gate.code or "AF-MEMORY-GATE-DENIED",
            gate.field or "record",
            gate.unlock or "resolve the gate failure and propose again",
            gate.reason,
        )
    if gate.verdict == "quarantine":
        return _quarantine_outcome(root, candidate, gate, now)
    directory = _directory(root)
    existing = _read(directory, _RECORDS, MemoryRecord)
    if any(
        item.content_sha256 == record.content_sha256 and item.outcome != "invalidated"
        for item in existing
    ):
        return MemoryOutcome(
            action="deduplicated",
            memory_id=record.memory_id,
            accepted=True,
            reason="same content hash already persisted",
            evidence_refs=record.evidence_refs,
        )
    persisted = record.model_copy(
        update={"outcome": "persisted", "freshness": "fresh", "created_at": now}
    )
    _append(directory, _RECORDS, persisted)
    return MemoryOutcome(
        action="accepted",
        memory_id=persisted.memory_id,
        accepted=True,
        reason="policy and evidence gates passed",
        evidence_refs=persisted.evidence_refs,
    )


def list_quarantine(root: Path) -> tuple[MemoryQuarantine, ...]:
    """All quarantine rows (pending and released) in append order."""
    return tuple(_read(_directory(root), _QUARANTINE, MemoryQuarantine))


def review_quarantine(
    root: Path,
    candidate_id: str,
    policy: MemoryPolicy,
    *,
    verdict: str,
    resolved_by: str,
    now: str,
) -> MemoryOutcome:
    """Human review of a quarantined candidate: persist or reject.

    "persist" re-runs the full gate pipeline — a reviewer can only release a
    candidate that the gates accept under the given (possibly revised) policy.
    The release is an append-only row; the original quarantine stays visible.
    """
    directory = _directory(root)
    rows = _read(directory, _QUARANTINE, MemoryQuarantine)
    pending = [
        row for row in rows if row.candidate_id == candidate_id and row.state == "quarantined"
    ]
    released = {row.quarantine_id for row in rows if row.state == "released"}
    pending = [row for row in pending if row.quarantine_id not in released]
    if not pending:
        return _refusal(
            "AF-MEMORY-QUARANTINE-NOT-FOUND",
            "candidate_id",
            "list quarantine rows for a pending candidate_id",
            f"no pending quarantine for candidate {candidate_id!r}",
        )
    row = pending[-1]
    release = MemoryQuarantine(
        quarantine_id=row.quarantine_id,
        candidate_id=candidate_id,
        memory_id=row.memory_id,
        state="released",
        verdict="persisted" if verdict == "persist" else "rejected",
        created_at=now,
        resolved_by=resolved_by,
    )
    if verdict == "persist":
        candidate = load_candidate(root, candidate_id)
        outcome = persist_candidate(root, candidate, policy, now=now)
        if outcome.accepted:
            _append(directory, _QUARANTINE, release)
        return outcome
    _append(directory, _QUARANTINE, release)
    return MemoryOutcome(
        action="rejected",
        memory_id=row.memory_id,
        accepted=False,
        code="AF-MEMORY-QUARANTINE-REJECTED",
        field="candidate_id",
        unlock="no action needed; the candidate never reached the record log",
        reason=f"quarantined candidate rejected by {resolved_by}",
    )


def load_candidate(root: Path, candidate_id: str) -> MemoryCandidate:
    candidates = _read(_directory(root), _CANDIDATES, MemoryCandidate)
    for candidate in candidates:
        if candidate.candidate_id == candidate_id:
            return candidate
    raise ValueError(f"AF-MEMORY-CANDIDATE-NOT-FOUND: {candidate_id}")


def _expired(record: MemoryRecord, now: str | None) -> bool:
    if not record.expires_at:
        return False
    if not now:
        return False
    try:
        return datetime.fromisoformat(record.expires_at) <= datetime.fromisoformat(now)
    except ValueError:
        return False


def query_memory(root: Path, query: MemoryQuery) -> MemoryRetrievalResult:
    directory = _directory(root)
    records = _read(directory, _RECORDS, MemoryRecord)
    invalidations = _read(directory, _INVALIDATIONS, MemoryInvalidation)
    invalidated_ids = {item.memory_id for item in invalidations}
    matches: list[MemoryRecord] = []
    stale_count = 0
    invalidated_count = 0
    unresolved: list[str] = []
    for record in records:
        if record.memory_id in invalidated_ids:
            invalidated_count += 1
            if not query.include_invalidated:
                continue
        if query.scopes and record.scope not in query.scopes:
            continue
        if (
            query.environment_fingerprint
            and record.environment_fingerprint != query.environment_fingerprint
        ):
            unresolved.append(f"environment_mismatch:{record.memory_id}")
            continue
        if query.environment and any(
            record.applicability.get(key) != value for key, value in query.environment.items()
        ):
            unresolved.append(f"environment_mismatch:{record.memory_id}")
            continue
        if _TRUST_ORDER[record.trust_level] < _TRUST_ORDER[query.minimum_trust]:
            continue
        searchable = json.dumps(record.payload, sort_keys=True, ensure_ascii=False).lower()
        if query.terms:
            coverage = sum(term.lower() in searchable for term in query.terms) / len(query.terms)
            if coverage < query.min_term_coverage:
                continue
        if record.expires_at and query.now is None:
            unresolved.append(f"AF-MEMORY-FRESHNESS-UNRESOLVED:{record.memory_id}")
        elif _expired(record, query.now):
            stale_count += 1
        matches.append(record)
    from apiforge.memory.retrieval import rank_records

    order = {score.memory_id: index for index, score in enumerate(rank_records(matches, query))}
    matches.sort(key=lambda item: order[item.memory_id])
    status = "ready"
    if unresolved or stale_count:
        status = "degraded"
    return MemoryRetrievalResult(
        query=query,
        records=tuple(matches[: query.max_results]),
        stale_count=stale_count,
        invalidated_count=invalidated_count,
        unresolved=tuple(unresolved),
        status=status,  # type: ignore[arg-type]
    )


def invalidate_memory(
    root: Path,
    memory_id: str,
    *,
    reason: str,
    invalidated_by: str,
    created_at: str,
    evidence_refs: tuple[str, ...] = (),
) -> MemoryOutcome:
    directory = _directory(root)
    records = _read(directory, _RECORDS, MemoryRecord)
    if not any(item.memory_id == memory_id for item in records):
        return _refusal(
            "AF-MEMORY-NOT-FOUND",
            "memory_id",
            "query the governed memory store for a valid id",
            f"memory {memory_id!r} is not present",
        )
    event = MemoryInvalidation(
        invalidation_id="invalidation:"
        + _digest({"memory_id": memory_id, "reason": reason, "created_at": created_at})[:16],
        memory_id=memory_id,
        reason=reason,
        invalidated_by=invalidated_by,
        created_at=created_at,
        evidence_refs=evidence_refs,
    )
    existing = _read(directory, _INVALIDATIONS, MemoryInvalidation)
    if any(item.invalidation_id == event.invalidation_id for item in existing):
        return MemoryOutcome(
            action="deduplicated",
            memory_id=memory_id,
            accepted=True,
            reason="invalidation already present",
        )
    _append(directory, _INVALIDATIONS, event)
    return MemoryOutcome(
        action="invalidated",
        memory_id=memory_id,
        accepted=True,
        reason=reason,
        evidence_refs=evidence_refs,
    )


def memory_store_digest(root: Path) -> str | None:
    """Return the current record log hash for receipts; no hash means no store."""
    path = _directory(root) / _RECORDS
    return sha256_file(path) if path.is_file() else None


__all__ = [
    "invalidate_memory",
    "list_quarantine",
    "load_candidate",
    "memory_store_digest",
    "persist_candidate",
    "propose_memory",
    "query_memory",
    "review_quarantine",
]
