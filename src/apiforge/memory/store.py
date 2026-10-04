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
from apiforge.core.io import sha256_file
from apiforge.core.models import JsonValue

_MEMORY_DIR = Path(".apiforge") / "memory"
_RECORDS = "records.jsonl"
_CANDIDATES = "candidates.jsonl"
_INVALIDATIONS = "invalidations.jsonl"
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


def persist_candidate(
    root: Path, candidate: MemoryCandidate, policy: MemoryPolicy, *, now: str
) -> MemoryOutcome:
    """Apply policy and evidence gates, then append an immutable record."""
    record = candidate.record
    if record.scope not in policy.allowed_scopes:
        return _refusal(
            "AF-MEMORY-SCOPE-DENIED",
            "scope",
            "use an allowed scope or have a human revise the MemoryPolicy",
            f"scope {record.scope!r} is not allowed by {policy.policy_id}",
        )
    if record.origin == "external_untrusted" and not policy.allow_external_untrusted:
        return _refusal(
            "AF-MEMORY-UNTRUSTED",
            "origin",
            "attach a trusted internal source and verified evidence",
            "external_untrusted content cannot be persisted by this policy",
        )
    if (
        record.scope in {"institutional", "semantic"}
        and policy.require_evidence_for_persistent
        and not record.evidence_refs
    ):
        return _refusal(
            "AF-MEMORY-EVIDENCE-REQUIRED",
            "evidence_refs",
            "provide evidence_refs from an independently verified artifact",
            "persistent cross-task memory requires evidence",
        )
    if record.origin == "model_generated" and not policy.allow_model_generated_persistent:
        return _refusal(
            "AF-MEMORY-MODEL-UNVERIFIED",
            "origin",
            "store as working/candidate data or attach verified evidence under policy",
            "model_generated content cannot be promoted automatically",
        )
    if _TRUST_ORDER[record.trust_level] < _TRUST_ORDER[policy.minimum_trust]:
        return _refusal(
            "AF-MEMORY-TRUST-INSUFFICIENT",
            "trust_level",
            "collect a stronger observation or lower policy only with explicit review",
            f"{record.trust_level} is below policy minimum {policy.minimum_trust}",
        )
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
        if _TRUST_ORDER[record.trust_level] < _TRUST_ORDER[query.minimum_trust]:
            continue
        searchable = json.dumps(record.payload, sort_keys=True, ensure_ascii=False).lower()
        if any(term.lower() not in searchable for term in query.terms):
            continue
        if record.expires_at and query.now is None:
            unresolved.append(f"AF-MEMORY-FRESHNESS-UNRESOLVED:{record.memory_id}")
        elif _expired(record, query.now):
            stale_count += 1
        matches.append(record)
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
    "load_candidate",
    "memory_store_digest",
    "persist_candidate",
    "propose_memory",
    "query_memory",
]
