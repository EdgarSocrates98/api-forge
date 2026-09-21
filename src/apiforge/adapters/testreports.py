"""Test report readers: pact / schemathesis / k6 / coverage -> test.* facts.

Each reader consumes the tool's standard report file offline — the tool
itself is never executed. Missing or malformed files are named
diagnostics, never guesses.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apiforge.adapters.inventory import CodeInventory
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_EXTRACTOR = "test-report"


def _diag(code: str, message: str, rel: str, digest: str | None) -> Diagnostic:
    source = (
        SourceRef(path=rel, sha256=digest, line=None, extractor=_EXTRACTOR)
        if digest is not None
        else None
    )
    return Diagnostic(code=code, status=FindingStatus.UNRESOLVED, message=message, source=source)


def _load(
    path: Path, rel: str, input_hashes: dict[str, str], diagnostics: list[Diagnostic]
) -> Any | None:
    if not path.is_file():
        diagnostics.append(_diag("AF-TEST-REPORT-MISSING", f"{rel} missing", rel, None))
        return None
    raw = path.read_bytes()
    input_hashes[rel] = hashlib.sha256(raw).hexdigest()
    try:
        return json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        diagnostics.append(
            _diag("AF-TEST-REPORT-INVALID", f"{rel}: not valid JSON ({exc})", rel, input_hashes[rel])
        )
        return None


def _fact(kind: str, rel: str, digest: str, measures: dict[str, Any], attrs: dict[str, Any]) -> Fact:
    return Fact(
        fact_id=stable_id("fact", {"kind": kind, "file": rel, **measures}),
        kind=kind,
        source=SourceRef(path=rel, sha256=digest, line=None, extractor=_EXTRACTOR),
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
        facts=tuple(facts),
        diagnostics=tuple(diagnostics),
        input_hashes=input_hashes,
    )


def extract_pact(path: Path) -> CodeInventory:
    """One pact contract file -> a `test.pact.contract` fact."""
    path = Path(path)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    doc = _load(path, path.name, hashes, diagnostics)
    if isinstance(doc, dict):
        interactions = doc.get("interactions") or []
        methods = sorted(
            {
                str(i.get("request", {}).get("method"))
                for i in interactions
                if isinstance(i, dict)
            }
            - {"None"}
        )
        paths = sorted(
            {
                str(i.get("request", {}).get("path"))
                for i in interactions
                if isinstance(i, dict)
            }
            - {"None"}
        )
        facts.append(
            _fact(
                "test.pact.contract",
                path.name,
                hashes[path.name],
                {"provider": str(doc.get("provider", {}).get("name", ""))},
                {
                    "consumer": doc.get("consumer", {}).get("name"),
                    "interactions": len(interactions),
                    "methods": methods,
                    "paths": paths,
                },
            )
        )
    return _inventory("pact", path.parent, facts, diagnostics, hashes)


def extract_schemathesis(path: Path) -> CodeInventory:
    """Schemathesis JSON report -> a `test.schemathesis.run` fact."""
    path = Path(path)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    doc = _load(path, path.name, hashes, diagnostics)
    if isinstance(doc, dict):
        totals = doc.get("totals") or {}
        checks: dict[str, Any] = {}
        total = ok = failure = 0
        for check, counts in totals.items():
            if not isinstance(counts, dict):
                continue
            c_total = int(counts.get("total") or 0)
            c_ok = int(counts.get("ok") or 0)
            c_fail = int(counts.get("failure") or 0)
            checks[str(check)] = {"total": c_total, "ok": c_ok, "failure": c_fail}
            total += c_total
            ok += c_ok
            failure += c_fail
        facts.append(
            _fact(
                "test.schemathesis.run",
                path.name,
                hashes[path.name],
                {"checks_total": total},
                {"checks": checks, "ok": ok, "failure": failure},
            )
        )
    return _inventory("schemathesis", path.parent, facts, diagnostics, hashes)


def extract_k6(path: Path) -> CodeInventory:
    """k6 --summary-export JSON -> a `test.k6.summary` fact."""
    path = Path(path)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    doc = _load(path, path.name, hashes, diagnostics)
    if isinstance(doc, dict):
        metrics = doc.get("metrics") or {}
        duration = metrics.get("http_req_duration") or {}
        failed = metrics.get("http_req_failed") or {}
        checks = metrics.get("checks") or {}
        facts.append(
            _fact(
                "test.k6.summary",
                path.name,
                hashes[path.name],
                {"vus_max": (metrics.get("vus_max") or {}).get("value")},
                {
                    "iterations": (metrics.get("iterations") or {}).get("count"),
                    "duration_avg_ms": duration.get("avg"),
                    "duration_p95_ms": duration.get("p(95)"),
                    "duration_p99_ms": duration.get("p(99)"),
                    "failed_rate": failed.get("rate"),
                    "checks_rate": checks.get("rate"),
                    "checks_failed": checks.get("fails"),
                },
            )
        )
    return _inventory("k6", path.parent, facts, diagnostics, hashes)


def extract_coverage(path: Path) -> CodeInventory:
    """coverage.py JSON -> a `test.coverage.py` fact."""
    path = Path(path)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    doc = _load(path, path.name, hashes, diagnostics)
    if isinstance(doc, dict):
        totals = doc.get("totals") or {}
        files = doc.get("files") or {}
        facts.append(
            _fact(
                "test.coverage.py",
                path.name,
                hashes[path.name],
                {"percent_covered": totals.get("percent_covered")},
                {
                    "num_statements": totals.get("num_statements"),
                    "missing_lines": totals.get("missing_lines"),
                    "files": len(files),
                },
            )
        )
    return _inventory("coverage", path.parent, facts, diagnostics, hashes)
