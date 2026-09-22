"""Profiler export readers: JFR JSON, pprof -top text, Pyroscope flamebearer.

The profilers themselves are never run — these read their standard exports.
Facts are capped at the top entries; a ``truncated`` attr records when the
profile held more than we emitted, so the cap is named, not silent.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from apiforge.adapters.inventory import CodeInventory
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_TOP_N = 20


def _fact(
    kind: str, rel: str, digest: str, measures: dict[str, Any], attrs: dict[str, Any]
) -> Fact:
    return Fact(
        fact_id=stable_id("fact", {"kind": kind, "file": rel, **measures}),
        kind=kind,
        source=SourceRef(path=rel, sha256=digest, extractor="profile"),
        measures=measures,
        attrs=attrs,
    )


def _inventory(
    framework: str,
    root: Path,
    facts: list[Fact],
    diagnostics: list[Diagnostic],
    input_hashes: dict[str, str],
) -> CodeInventory:
    return CodeInventory(
        framework=framework,
        root=str(root),
        diagnostics=tuple(diagnostics),
        facts=tuple(facts),
        input_hashes=input_hashes,
    )


def _bad(path: Path, framework: str, code: str, message: str) -> CodeInventory:
    digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "0" * 64
    return _inventory(
        framework,
        path.parent,
        [],
        [
            Diagnostic(
                code=code,
                status=FindingStatus.UNRESOLVED,
                message=message,
                source=SourceRef(path=path.name, sha256=digest, extractor="profile"),
            )
        ],
        {path.name: digest},
    )


def _load_json(path: Path, framework: str, code: str) -> tuple[Any, CodeInventory | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return None, _bad(path, framework, code, str(exc))


def extract_jfr(path: Path) -> CodeInventory:
    """`jfr print --json` output -> perf.jfr.event counts + top frames."""
    path = Path(path)
    doc, bad = _load_json(path, "jfr", "AF-PERF-REPORT-INVALID")
    if bad:
        return bad
    events = ((doc or {}).get("recording") or {}).get("events")
    if not isinstance(events, list):
        return _bad(path, "jfr", "AF-PERF-REPORT-INVALID", "missing recording.events")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    by_type: Counter[str] = Counter()
    frames: Counter[str] = Counter()
    for event in events:
        if not isinstance(event, dict):
            continue
        etype = str(event.get("type", "unknown"))
        by_type[etype] += 1
        if etype == "jdk.ExecutionSample":
            stack = ((event.get("values") or {}).get("stackTrace") or {}).get("frames") or []
            if stack and isinstance(stack[0], dict):
                method = stack[0].get("method") or {}
                name = f"{method.get('type', '?')}.{method.get('name', '?')}"
                frames[name] += 1
    facts = [
        _fact(
            "perf.jfr.recording",
            path.name,
            digest,
            {"events": len(events)},
            {"by_type": dict(sorted(by_type.items()))},
        )
    ]
    top = frames.most_common(_TOP_N)
    for name, count in top:
        facts.append(
            _fact(
                "perf.jfr.frame",
                path.name,
                digest,
                {"frame": name},
                {"execution_samples": count, "truncated": len(frames) > _TOP_N},
            )
        )
    return _inventory("jfr", path.parent, facts, [], {path.name: digest})


_PPROF_ROW = re.compile(
    r"^\s*([\d.]+)(ms|s|ns|us)?\s+[\d.]+%\s+[\d.]+%\s+([\d.]+)(ms|s|ns|us)?\s+[\d.]+%\s+(\S+)\s*$"
)


def extract_pprof(path: Path) -> CodeInventory:
    """`go tool pprof -top` text -> perf.pprof.entry facts."""
    path = Path(path)
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        return _bad(path, "pprof", "AF-PERF-REPORT-INVALID", str(exc))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    rows: list[tuple[str, float, float]] = []
    for line in lines:
        if m := _PPROF_ROW.match(line):
            flat, _, cum, _, name = m.groups()
            rows.append((name, float(flat), float(cum)))
    if not rows:
        return _bad(path, "pprof", "AF-PERF-REPORT-INVALID", "no -top rows recognized")
    facts = [
        _fact(
            "perf.pprof.top",
            path.name,
            digest,
            {"entries": len(rows)},
            {"truncated": len(rows) > _TOP_N},
        )
    ]
    for name, flat, cum in rows[:_TOP_N]:
        facts.append(
            _fact(
                "perf.pprof.entry",
                path.name,
                digest,
                {"function": name},
                {"flat": flat, "cum": cum},
            )
        )
    return _inventory("pprof", path.parent, facts, [], {path.name: digest})


def extract_pyroscope(path: Path) -> CodeInventory:
    """Pyroscope flamebearer JSON -> perf.pyroscope.entry facts."""
    path = Path(path)
    doc, bad = _load_json(path, "pyroscope", "AF-PERF-REPORT-INVALID")
    if bad:
        return bad
    fb = (doc or {}).get("flamebearer") or {}
    names = fb.get("names")
    levels = fb.get("levels")
    if not isinstance(names, list) or not isinstance(levels, list):
        return _bad(path, "pyroscope", "AF-PERF-REPORT-INVALID", "missing flamebearer levels")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    self_samples: Counter[str] = Counter()
    total_samples: Counter[str] = Counter()
    for level in levels:
        if not isinstance(level, list):
            continue
        # flamebearer bars pack four ints: [offset, total, self, name_idx].
        for i in range(0, len(level) - 3, 4):
            total_v, self_v, name_idx = level[i + 1], level[i + 2], level[i + 3]
            if isinstance(name_idx, int) and 0 <= name_idx < len(names):
                name = str(names[name_idx])
                if isinstance(self_v, (int, float)):
                    self_samples[name] += int(self_v)
                if isinstance(total_v, (int, float)):
                    total_samples[name] += int(total_v)
    top = self_samples.most_common(_TOP_N)
    facts = [
        _fact(
            "perf.pyroscope.top",
            path.name,
            digest,
            {"symbols": len(names)},
            {"entries": len(top), "truncated": len(self_samples) > _TOP_N},
        )
    ]
    for name, self_v in top:
        facts.append(
            _fact(
                "perf.pyroscope.entry",
                path.name,
                digest,
                {"function": name},
                {"self": self_v, "total": total_samples.get(name, self_v)},
            )
        )
    return _inventory("pyroscope", path.parent, facts, [], {path.name: digest})
