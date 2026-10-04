"""A bounded JSONL blackboard; entries are data, not instructions."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import cast

from apiforge.contracts.agentic_memory import (
    BlackboardEntry,
    BlackboardKind,
    BlackboardQuery,
    BlackboardResult,
    MemoryOrigin,
    TrustLevel,
)
from apiforge.core.models import JsonValue

_FILE = Path(".apiforge") / "blackboard" / "entries.jsonl"


def _path(root: Path) -> Path:
    resolved = Path(root).resolve()
    if resolved.name == ".apiforge":
        resolved = resolved.parent
    return resolved / _FILE


def _digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _read(path: Path) -> list[BlackboardEntry]:
    if not path.is_file():
        return []
    rows: list[BlackboardEntry] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(BlackboardEntry.model_validate(json.loads(line)))
        except (json.JSONDecodeError, ValueError) as exc:
            raise ValueError(f"AF-BLACKBOARD-STORE-CORRUPT: {path}:{line_no}: {exc}") from exc
    return rows


def append_entry(
    root: Path,
    *,
    task_id: str,
    scope: str,
    kind: str,
    origin: str,
    payload: object,
    created_at: str,
    trust_level: str = "unknown",
    taint: tuple[str, ...] = (),
    provenance: tuple[str, ...] = (),
    evidence_refs: tuple[str, ...] = (),
    supersedes: tuple[str, ...] = (),
) -> BlackboardEntry:
    body = {
        "task_id": task_id, "scope": scope, "kind": kind, "origin": origin,
        "payload": payload, "created_at": created_at, "provenance": provenance,
    }
    entry = BlackboardEntry(
        entry_id="blackboard:" + _digest(body)[:16],
        task_id=task_id, scope=scope, kind=cast(BlackboardKind, kind), origin=cast(MemoryOrigin, origin),
        payload=cast(JsonValue, payload), created_at=created_at,
        trust_level=cast(TrustLevel, trust_level), taint=taint,
        provenance=provenance, evidence_refs=evidence_refs, supersedes=supersedes,
        content_sha256=_digest(payload),
    )
    path = _path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = _read(path)
    if not any(item.entry_id == entry.entry_id for item in existing):
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(entry.model_dump(mode="json"), sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n")
    return entry


def query_entries(root: Path, query: BlackboardQuery) -> BlackboardResult:
    rows = _read(_path(root))
    matches: list[BlackboardEntry] = []
    unresolved: list[str] = []
    for entry in rows:
        if entry.task_id != query.task_id:
            continue
        if query.kinds and entry.kind not in query.kinds:
            continue
        if query.scope and entry.scope != query.scope:
            continue
        searchable = json.dumps(entry.payload, sort_keys=True, ensure_ascii=False).lower()
        if any(term.lower() not in searchable for term in query.terms):
            continue
        if entry.taint:
            unresolved.append(f"tainted:{entry.entry_id}")
        matches.append(entry)
    return BlackboardResult(
        query=query, entries=tuple(matches[-query.max_results:]), unresolved=tuple(unresolved),
        status="degraded" if unresolved else "ready",
    )


__all__ = ["append_entry", "query_entries"]
