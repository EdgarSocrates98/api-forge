"""Run attribution rows in ``economy.jsonl``: who spent the bytes, and why.

Attribution rows carry ``payload_bytes: 0`` because the transport bytes of the
same emission are already recorded by the emitting verb's legacy row; this
keeps ``economy report`` totals unchanged. ``stats`` aggregates attribution by
run and source; ``explain`` answers from recorded provenance rules only.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy import RunLedgerEntry
from apiforge.economy.ledger import ledger_path

ENTRY_SCHEMA = "apiforge/run-ledger-entry/v1"


class EconomyError(ContractError):
    def __init__(self, code: str, detail: str, *, field: str, unlock: str) -> None:
        super().__init__(code, detail)
        self.field = field
        self.unlock = unlock


PERSIST_FAILURE = "AF-ECONOMY-LEDGER-PERSIST"
FAILURES_NAME = "economy.persist-failures"


def append(
    root: Path,
    entry: RunLedgerEntry,
    *,
    auditable: bool = False,
    recorded_at: str | None = None,
) -> bool:
    """Append one attribution row and report whether it was persisted.

    Best-effort telemetry (``auditable=False``) swallows I/O failure like the
    legacy recorder. An auditable row that cannot be written is recorded in
    ``economy.persist-failures`` (when possible) and the caller must surface
    ``AF-ECONOMY-LEDGER-PERSIST`` as unresolved; a lost row is never silent.

    ``recorded_at`` is the append instant — observed, never synthesized after
    the fact. Callers may pass an authoritative timestamp; otherwise the write
    time is stamped here so new rows carry real temporal evidence.
    """
    stamp = recorded_at or entry.recorded_at or datetime.now(UTC).isoformat()
    if entry.recorded_at != stamp:
        entry = entry.model_copy(update={"recorded_at": stamp})
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
        if auditable:
            try:
                marker = ledger_path(root).parent / FAILURES_NAME
                with marker.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps({"run_id": entry.run_id, "verb": entry.verb}) + "\n")
            except OSError:
                pass
        return False
    return True


def persist_failures(root: Path, run_id: str | None = None) -> int:
    """Lost auditable rows, for one run when ``run_id`` is given, else for the whole root."""
    marker = ledger_path(root).parent / FAILURES_NAME
    try:
        lines = [line for line in marker.read_text(encoding="utf-8").splitlines() if line.strip()]
    except OSError:
        return 0
    if run_id is None:
        return len(lines)
    count = 0
    for line in lines:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and row.get("run_id") == run_id:
            count += 1
    return count


ELIGIBILITY_FILE = Path(__file__).resolve().parents[1] / "rules" / "token_eligibility.yaml"


@lru_cache(maxsize=2)
def eligible_prefixes(path: str = str(ELIGIBILITY_FILE)) -> tuple[str, ...]:
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        if raw.get("schema") != "apiforge/token-eligibility/v1":
            raise ValueError("schema must be apiforge/token-eligibility/v1")
        prefixes = raw.get("verb_prefixes")
        if not isinstance(prefixes, list) or not prefixes:
            raise ValueError("verb_prefixes must be a non-empty list")
        if not all(isinstance(item, str) and item.strip() for item in prefixes):
            raise ValueError("verb_prefixes must be non-blank strings")
        if len(set(prefixes)) != len(prefixes):
            raise ValueError("verb_prefixes must be unique")
    except (OSError, yaml.YAMLError, ValueError, AttributeError) as exc:
        raise EconomyError(
            "AF-ECONOMY-TOKEN-RULE-INVALID",
            f"{path}: {exc}",
            field="rules",
            unlock="restore rules/token_eligibility.yaml",
        ) from exc
    return tuple(prefixes)


def is_token_eligible(row: RunLedgerEntry) -> bool:
    """Model-facing rows (declared verb prefixes) or any row that carries measured tokens."""
    return row.cost.observed_tokens is not None or row.verb.startswith(eligible_prefixes())


def token_coverage(rows: list[RunLedgerEntry]) -> dict[str, Any]:
    """Only token-eligible rows count; a total is ``observed`` only when all of them are measured."""
    eligible_rows = [row for row in rows if is_token_eligible(row)]
    eligible = len(eligible_rows)
    observed = sum(1 for row in eligible_rows if row.cost.observed_tokens is not None)
    if observed == 0:
        status = "unresolved"
    elif observed == eligible:
        status = "complete"
    else:
        status = "partial"
    return {"status": status, "observed_rows": observed, "eligible_rows": eligible}


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
    for row in rows:
        for bucket in (
            by_source.setdefault(row.source, _zero()),
            by_run.setdefault(row.run_id, _zero()),
            total,
        ):
            _add(bucket, row)
    attributed = total["context_bytes"] + total["tool_result_bytes"]
    coverage = token_coverage(rows)
    failures_global = persist_failures(root)
    failures = persist_failures(root, run_id) if run_id is not None else failures_global
    return {
        "schema": "apiforge/economy-stats/v1",
        "runs": len(by_run),
        "entries": len(rows),
        "total": total,
        "attributed_bytes": attributed,
        "by_source": dict(sorted(by_source.items())),
        "by_run": dict(sorted(by_run.items())),
        "legacy": {key: legacy[key] for key in ("calls", "payload_bytes")},
        "observed_tokens": (
            total["observed_tokens"] if coverage["status"] == "complete" else coverage["status"]
        ),
        "observed_tokens_measured": total["observed_tokens"],
        "token_coverage": coverage,
        "tokens_unresolved": coverage["status"] != "complete",
        "persist_failures": failures,
        "persist_failures_for_run": failures if run_id is not None else None,
        "persist_failures_global": failures_global,
        "unresolved": [PERSIST_FAILURE] if failures else [],
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
