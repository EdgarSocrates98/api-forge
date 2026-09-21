"""Append-only economy ledger at ``<root>/.apiforge/economy.jsonl``.

Each emitted payload is recorded as ``{verb, detail_level, payload_bytes}``.
Recording is best-effort: a write failure records nothing and never breaks
the call it was measuring. Tokens are only real with a provider transcript —
without one the report carries ``tokens_unresolved: true``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LEDGER_NAME = "economy.jsonl"


def ledger_path(root: Path) -> Path:
    return Path(root) / ".apiforge" / LEDGER_NAME


def record(root: Path, *, verb: str, detail_level: str, payload_bytes: int) -> None:
    """Append one entry; swallow I/O failure — measurement never breaks the call."""
    try:
        path = ledger_path(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "verb": verb,
                        "detail_level": detail_level,
                        "payload_bytes": payload_bytes,
                    },
                    sort_keys=True,
                )
                + "\n"
            )
    except OSError:
        return


def _bucket() -> dict[str, int]:
    return {"calls": 0, "payload_bytes": 0}


def _add(bucket: dict[str, int], payload_bytes: int) -> None:
    bucket["calls"] += 1
    bucket["payload_bytes"] += payload_bytes


def report(root: Path) -> dict[str, Any]:
    """Aggregate the ledger under ``root``; an absent ledger reports zero calls."""
    path = ledger_path(root)
    entries: list[dict[str, Any]] = []
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                entries.append(json.loads(line))

    by_verb: dict[str, dict[str, int]] = {}
    by_level: dict[str, dict[str, int]] = {}
    per_verb_level: dict[str, dict[str, int]] = {}
    total = _bucket()
    for e in entries:
        verb = str(e.get("verb", "unknown"))
        level = str(e.get("detail_level", "normal"))
        size = int(e.get("payload_bytes", 0))
        _add(total, size)
        _add(by_verb.setdefault(verb, _bucket()), size)
        _add(by_level.setdefault(level, _bucket()), size)
        levels = per_verb_level.setdefault(verb, {})
        levels[level] = levels.get(level, 0) + size

    detail_level_effect = {
        verb: {
            "summary_bytes": levels["summary"],
            "normal_bytes": levels["normal"],
            "saved_bytes": levels["normal"] - levels["summary"],
        }
        for verb, levels in sorted(per_verb_level.items())
        if "summary" in levels and "normal" in levels
    }
    return {
        "calls": total["calls"],
        "payload_bytes": total["payload_bytes"],
        "by_verb": dict(sorted(by_verb.items())),
        "by_level": dict(sorted(by_level.items())),
        "detail_level_effect": detail_level_effect,
        "tokens_unresolved": True,
        "ledger": str(path),
    }
