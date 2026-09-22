"""Append-only PerformanceRun memory — `search_performance_memory` local store.

Runs persist as canonical JSON lines under
``<root>/.apiforge/perf/runs.jsonl``. Each record carries the sha256 of the
stored payload plus the declared ``recorded_at`` (explicit, never read from
the clock). Search filters only declared fields — ``subject``, ``tool`` and
a ``since`` window over ``recorded_at`` — and never infers a match. A
corrupt line is named, not skipped: the file is the record.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apiforge.contracts.stubs import PerformanceRun


class MemoryError(ValueError):
    """A refused memory operation; ``str()`` begins with the AF code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


def _runs_path(root: Path) -> Path:
    return Path(root) / ".apiforge" / "perf" / "runs.jsonl"


def _canonical(run: PerformanceRun) -> str:
    return json.dumps(
        run.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
    )


def _tool_of(run: PerformanceRun) -> str | None:
    """Declared tool identity — produced_by, or attributes.tool when present."""
    tool = run.attributes.get("tool")
    if isinstance(tool, str) and tool:
        return tool
    return run.produced_by or None


def add_run(
    root: Path, run: PerformanceRun, *, recorded_at: str | None = None
) -> dict[str, Any]:
    """Append a run to the memory store; returns the stored record's keys."""
    payload = run.model_dump(mode="json")
    digest = hashlib.sha256(_canonical(run).encode()).hexdigest()
    record = {
        "recorded_at": recorded_at,
        "sha256": digest,
        "subject": run.subject,
        "tool": _tool_of(run),
        "run": payload,
    }
    path = _runs_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(
            json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n"
        )
    return {
        "path": str(path),
        "recorded_at": recorded_at,
        "sha256": digest,
        "subject": run.subject,
        "tool": record["tool"],
    }


def read_runs(root: Path) -> list[dict[str, Any]]:
    """Read every stored record; a corrupt line is named, never skipped."""
    path = _runs_path(root)
    if not path.is_file():
        return []
    records: list[dict[str, Any]] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for lineno, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            PerformanceRun.model_validate(record["run"])
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            raise MemoryError(
                "AF-PERF-MEMORY-CORRUPT",
                f"{path}:{lineno} of {len(lines)} lines unreadable ({exc})",
            ) from exc
        records.append(record)
    return records


def search_runs(
    root: Path,
    *,
    subject: str | None = None,
    tool: str | None = None,
    since: str | None = None,
) -> list[dict[str, Any]]:
    """Filter stored runs by declared fields only — zero results on no match.

    ``since`` compares ``recorded_at`` lexicographically (ISO-8601 strings);
    records without ``recorded_at`` never satisfy a ``since`` filter.
    """
    out: list[dict[str, Any]] = []
    for record in read_runs(root):
        if subject is not None and record.get("subject") != subject:
            continue
        if tool is not None and record.get("tool") != tool:
            continue
        if since is not None:
            recorded = record.get("recorded_at")
            if not isinstance(recorded, str) or recorded < since:
                continue
        out.append(record)
    return out
