"""Advisory invalidation planning for the §16 trigger taxonomy.

`suggest_invalidations` only *plans*: it names candidate memory_ids plus a
per-item rationale. The actual invalidation still flows through
`invalidate_memory` as an append-only event — nothing here mutates the store.
"""

from __future__ import annotations

import json
from pathlib import Path

from apiforge.contracts.agentic_memory import MemoryInvalidation, MemoryRecord
from apiforge.contracts.trust import (
    MemoryInvalidationPlan,
    MemoryInvalidationTrigger,
)


def _haystack(record: MemoryRecord) -> str:
    return json.dumps(
        {
            "provenance": record.provenance,
            "evidence_refs": record.evidence_refs,
            "applicability": record.applicability,
        },
        sort_keys=True,
        ensure_ascii=False,
    ).lower()


def suggest_invalidations(
    root: Path,
    trigger: MemoryInvalidationTrigger,
    *,
    environment_fingerprint: str | None = None,
    changed: tuple[str, ...] = (),
    memory_ids: tuple[str, ...] = (),
) -> MemoryInvalidationPlan:
    """Name the records a trigger probably invalidates, with rationale."""
    from apiforge.memory.store import _INVALIDATIONS, _RECORDS, _directory, _read

    directory = _directory(root)
    records = _read(directory, _RECORDS, MemoryRecord)
    invalidations = _read(directory, _INVALIDATIONS, MemoryInvalidation)
    live = {
        item.memory_id
        for item in records
        if item.memory_id not in {i.memory_id for i in invalidations}
    }
    rationale: dict[str, str] = {}
    unresolved: list[str] = []
    if trigger in {"runtime_change", "framework_change"}:
        if environment_fingerprint is None:
            unresolved.append("environment_fingerprint required to plan environment triggers")
        else:
            for record in records:
                if record.memory_id not in live or record.environment_fingerprint is None:
                    continue
                if record.environment_fingerprint != environment_fingerprint:
                    rationale[record.memory_id] = (
                        f"record environment {record.environment_fingerprint!r} predates "
                        f"current {environment_fingerprint!r}"
                    )
    elif trigger in {"source_change", "contract_change", "policy_change", "dependency_change"}:
        if not changed:
            unresolved.append("changed identifiers required to plan source/dependency triggers")
        needles = [item.lower() for item in changed]
        for record in records:
            if record.memory_id not in live:
                continue
            haystack = _haystack(record)
            hits = [item for item in needles if item in haystack]
            if hits:
                rationale[record.memory_id] = (
                    f"{trigger} touched dependency/provenance {sorted(hits)}"
                )
    elif trigger in {"contradicting_evidence", "outcome_invalid"}:
        if not memory_ids:
            unresolved.append("explicit memory_ids required for evidence/outcome triggers")
        known = {item.memory_id for item in records}
        for memory_id in memory_ids:
            if memory_id in live:
                rationale[memory_id] = f"{trigger} reported for this record"
            elif memory_id not in known:
                unresolved.append(f"unknown memory_id {memory_id!r}")
    return MemoryInvalidationPlan(
        trigger=trigger,
        memory_ids=tuple(sorted(rationale)),
        rationale=rationale,
        unresolved=tuple(unresolved),
    )


__all__ = ["suggest_invalidations"]
