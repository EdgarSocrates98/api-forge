"""Run attribution rows in ``economy.jsonl``: who spent the bytes, and why.

Attribution rows carry ``payload_bytes: 0`` because the transport bytes of the
same emission are already recorded by the emitting verb's legacy row; this
keeps ``economy report`` totals unchanged. ``stats`` aggregates attribution by
run and source; ``explain`` answers from recorded provenance rules only.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy import RunLedgerEntry
from apiforge.economy.ledger import ledger_path

ENTRY_SCHEMA = "apiforge/run-ledger-entry/v1"


class EconomyError(ContractError):
    def __init__(self, code: str, detail: str, *, field: str, unlock: str) -> None:
        super().__init__(code, detail)
        self.field = field
        self.unlock = unlock


def append(root: Path, entry: RunLedgerEntry) -> None:
    """Append one attribution row; swallow I/O failure like the legacy recorder."""
    row = {
        "verb": entry.verb,
        "detail_level": entry.detail_level,
        "payload_bytes": 0,
        **entry.model_dump(mode="json"),
    }
    try:
        path = ledger_path(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    except OSError:
        return


def entries(root: Path) -> tuple[list[RunLedgerEntry], dict[str, int]]:
    """Read attribution rows; legacy rows are counted, malformed rows are skipped."""
    parsed: list[RunLedgerEntry] = []
    legacy = {"calls": 0, "payload_bytes": 0, "malformed_lines": 0}
    for row in _rows(root, legacy):
        if row.get("schema") == ENTRY_SCHEMA:
            try:
                parsed.append(
                    RunLedgerEntry.model_validate(
                        {key: value for key, value in row.items() if key != "payload_bytes"}
                    )
                )
            except ValueError:
                legacy["malformed_lines"] += 1
        else:
            legacy["calls"] += 1
            legacy["payload_bytes"] += int(row.get("payload_bytes", 0) or 0)
    return parsed, legacy


def stats(root: Path, *, run_id: str | None = None) -> dict[str, Any]:
    rows, legacy = entries(root)
    if run_id is not None:
        rows = [row for row in rows if row.run_id == run_id]
    by_source: dict[str, dict[str, int]] = {}
    by_run: dict[str, dict[str, int]] = {}
    total = _zero()
    tokens_seen = False
    for row in rows:
        for bucket in (
            by_source.setdefault(row.source, _zero()),
            by_run.setdefault(row.run_id, _zero()),
            total,
        ):
            _add(bucket, row)
        tokens_seen = tokens_seen or row.cost.observed_tokens is not None
    attributed = total["context_bytes"] + total["tool_result_bytes"]
    return {
        "schema": "apiforge/economy-stats/v1",
        "runs": len(by_run),
        "entries": len(rows),
        "total": total,
        "attributed_bytes": attributed,
        "by_source": dict(sorted(by_source.items())),
        "by_run": dict(sorted(by_run.items())),
        "legacy": {key: legacy[key] for key in ("calls", "payload_bytes")},
        "observed_tokens": total["observed_tokens"] if tokens_seen else "unresolved",
        "tokens_unresolved": not tokens_seen,
        "diagnostics": {"malformed_lines": legacy["malformed_lines"]},
        "ledger": str(ledger_path(root)),
    }


def explain(root: Path, run_id: str) -> dict[str, Any]:
    rows = [row for row in entries(root)[0] if row.run_id == run_id]
    if not rows:
        raise EconomyError(
            "AF-ECONOMY-RUN-NOT-FOUND",
            f"no attribution rows for {run_id!r} in {ledger_path(root)}",
            field="run_id",
            unlock="pass a run_id printed by `apiforge context capsule` or `economy stats`",
        )
    reasons: dict[str, dict[str, Any]] = {}
    spent: dict[str, int] = {}
    for row in rows:
        spent[row.source] = (
            spent.get(row.source, 0) + row.cost.context_bytes + row.cost.tool_result_bytes
        )
        for ref in row.refs:
            item = reasons.setdefault(
                ref.uri,
                {
                    "uri": ref.uri,
                    "label": ref.label,
                    "source": row.source,
                    "rule": ref.provenance,
                    "reason": reason(ref.provenance),
                    "bytes": 0,
                    "verbs": [],
                },
            )
            item["bytes"] += ref.size_bytes
            if row.verb not in item["verbs"]:
                item["verbs"].append(row.verb)
    total = sum(spent.values())
    return {
        "schema": "apiforge/economy-explain/v1",
        "run_id": run_id,
        "total_bytes": total,
        "by_source": {
            source: {"bytes": size, "share": round(size / total, 4) if total else 0.0}
            for source, size in sorted(spent.items())
        },
        "refs": sorted(
            reasons.values(), key=lambda item: (-int(item["bytes"]), str(item["label"]))
        ),
        "method": "recorded provenance rules; no model call",
    }


def reason(provenance: str) -> str:
    kind, _, detail = provenance.partition(":")
    rules = {
        "target": "the requested operation itself",
        "schema-ref": f"referenced by the target contract ($ref {detail})",
        "schema-model": f"code model mirroring schema {detail}; carried as parity/delta",
        "graph-edge": f"graph edge {detail} reached from the target",
        "symbol-match": f"test file mentions handler {detail}",
        "expand": f"expanded on demand ({detail})",
    }
    return rules.get(kind, provenance)


def _rows(root: Path, legacy: dict[str, int]) -> Iterator[dict[str, Any]]:
    path = ledger_path(root)
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            legacy["malformed_lines"] += 1
            continue
        if isinstance(row, dict):
            yield row
        else:
            legacy["malformed_lines"] += 1


def _zero() -> dict[str, int]:
    return {
        "context_bytes": 0,
        "tool_result_bytes": 0,
        "expansions": 0,
        "cache_hits": 0,
        "duration_ms": 0,
        "observed_tokens": 0,
    }


def _add(bucket: dict[str, int], row: RunLedgerEntry) -> None:
    cost = row.cost
    bucket["context_bytes"] += cost.context_bytes
    bucket["tool_result_bytes"] += cost.tool_result_bytes
    bucket["expansions"] += cost.expansions
    bucket["cache_hits"] += cost.cache_hits
    bucket["duration_ms"] += cost.duration_ms
    bucket["observed_tokens"] += cost.observed_tokens or 0


__all__ = ["EconomyError", "append", "entries", "explain", "reason", "stats"]
