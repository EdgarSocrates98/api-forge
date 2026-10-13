"""Test report readers: pact / schemathesis / k6 / coverage -> test.* facts.

Each reader consumes the tool's standard report file offline — the tool
itself is never executed. Missing or malformed files are named
diagnostics, never guesses.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
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
            _diag(
                "AF-TEST-REPORT-INVALID", f"{rel}: not valid JSON ({exc})", rel, input_hashes[rel]
            )
        )
        return None


def _fact(
    kind: str, rel: str, digest: str, measures: dict[str, Any], attrs: dict[str, Any]
) -> Fact:
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
            {str(i.get("request", {}).get("method")) for i in interactions if isinstance(i, dict)}
            - {"None"}
        )
        paths = sorted(
            {str(i.get("request", {}).get("path")) for i in interactions if isinstance(i, dict)}
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
        reqs = metrics.get("http_reqs") or {}
        iters = metrics.get("iterations") or {}
        dropped = metrics.get("dropped_iterations") or {}
        facts.append(
            _fact(
                "test.k6.summary",
                path.name,
                hashes[path.name],
                {
                    "vus_max": (metrics.get("vus_max") or {}).get("value"),
                    # RPS and TPS are distinct measures: http_reqs.rate counts
                    # requests, iterations.rate counts completed scenario
                    # iterations — TPS only when the script declares one
                    # business transaction per iteration (a PerformanceRun
                    # field, never inferred here).
                    "rps": reqs.get("rate"),
                    "iterations_rate": iters.get("rate"),
                    "dropped_iterations": dropped.get("count"),
                },
                {
                    "iterations": iters.get("count"),
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


def _load_text(
    path: Path, rel: str, input_hashes: dict[str, str], diagnostics: list[Diagnostic]
) -> str | None:
    if not path.is_file():
        diagnostics.append(_diag("AF-TEST-REPORT-MISSING", f"{rel} missing", rel, None))
        return None
    raw = path.read_bytes()
    input_hashes[rel] = hashlib.sha256(raw).hexdigest()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        diagnostics.append(
            _diag("AF-TEST-REPORT-INVALID", f"{rel}: not UTF-8 ({exc})", rel, input_hashes[rel])
        )
        return None


def _percentile(values: list[float], pct: float) -> float | None:
    """Nearest-rank percentile — deterministic, never interpolated."""
    if not values:
        return None
    ordered = sorted(values)
    idx = max(0, min(len(ordered) - 1, int(len(ordered) * pct / 100 + 0.9999) - 1))
    return ordered[idx]


def extract_locust(path: Path) -> CodeInventory:
    """Locust ``--csv`` stats export -> a `test.locust.summary` fact.

    Reads the ``Aggregated`` row when present; otherwise sums the per-name
    rows. RPS and failure rate come straight from the export — the tool
    measured them.
    """
    path = Path(path)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    text = _load_text(path, path.name, hashes, diagnostics)
    facts: list[Fact] = []
    if text is not None:
        rows = list(csv.DictReader(io.StringIO(text)))
        agg = next((r for r in rows if (r.get("Name") or "") == "Aggregated"), None)
        if agg is None and rows:
            agg = rows[-1]  # last row is the aggregate in older exports
        if agg is not None:

            def num(key: str) -> float | None:
                try:
                    return float(agg.get(key) or 0)
                except ValueError:
                    return None

            facts.append(
                _fact(
                    "test.locust.summary",
                    path.name,
                    hashes[path.name],
                    {"requests": num("Request Count"), "failures": num("Failure Count")},
                    {
                        "rps": num("Requests/s"),
                        "avg_ms": num("Average Response Time"),
                        "p95_ms": num("95%"),
                        "p99_ms": num("99%"),
                        "rows_aggregated": len(rows),
                    },
                )
            )
    return _inventory("locust", path.parent, facts, diagnostics, hashes)


def extract_jmeter(path: Path) -> CodeInventory:
    """JMeter JTL CSV -> a `test.jmeter.summary` fact.

    JTL is per-sample; we aggregate count, error rate and percentiles of
    the ``elapsed`` column — TPS is never inferred from samples.
    """
    path = Path(path)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    text = _load_text(path, path.name, hashes, diagnostics)
    facts: list[Fact] = []
    if text is not None:
        rows = list(csv.DictReader(io.StringIO(text)))
        elapsed = [
            float(r["elapsed"]) for r in rows if r.get("elapsed", "").replace(".", "", 1).isdigit()
        ]
        failures = sum(1 for r in rows if (r.get("success") or "").strip() in ("false", "0"))
        if rows:
            facts.append(
                _fact(
                    "test.jmeter.summary",
                    path.name,
                    hashes[path.name],
                    {
                        "samples": len(rows),
                        "errors": failures,
                        "error_rate": failures / len(rows),
                    },
                    {
                        "avg_ms": sum(elapsed) / len(elapsed) if elapsed else None,
                        "p95_ms": _percentile(elapsed, 95),
                        "p99_ms": _percentile(elapsed, 99),
                        "labels": sorted({r.get("label", "") for r in rows} - {""}),
                    },
                )
            )
    return _inventory("jmeter", path.parent, facts, diagnostics, hashes)


def extract_gatling(path: Path) -> CodeInventory:
    """Gatling ``global_stats.json`` -> a `test.gatling.summary` fact.

    Accepts the file itself or the report directory containing
    ``js/global_stats.json``.
    """
    path = Path(path)
    if path.is_dir():
        path = path / "js" / "global_stats.json"
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    doc = _load(path, path.name, hashes, diagnostics)
    facts: list[Fact] = []
    if isinstance(doc, dict):

        def stat(key: str) -> float | None:
            v = doc.get(key)
            if isinstance(v, dict):
                v = v.get("total")
            if isinstance(v, (int, float)):
                return float(v)
            return None

        facts.append(
            _fact(
                "test.gatling.summary",
                path.name,
                hashes[path.name],
                {
                    "requests": stat("numberOfRequests"),
                    "mean_ms": stat("meanResponseTime"),
                    "p95_ms": stat("percentiles3"),
                    "p99_ms": stat("percentiles4"),
                },
                {"max_ms": stat("maxResponseTime"), "std_dev": stat("standardDeviation")},
            )
        )
    return _inventory("gatling", path.parent, facts, diagnostics, hashes)


def extract_vegeta(path: Path) -> CodeInventory:
    """`vegeta report -type=json` -> a `test.vegeta.summary` fact."""
    path = Path(path)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    doc = _load(path, path.name, hashes, diagnostics)
    facts: list[Fact] = []
    if isinstance(doc, dict):
        lat = doc.get("latencies") or {}
        facts.append(
            _fact(
                "test.vegeta.summary",
                path.name,
                hashes[path.name],
                {
                    "requests": doc.get("requests"),
                    "rate": doc.get("rate"),
                    "success_rate": doc.get("success"),
                },
                {
                    # vegeta latencies are nanoseconds -> ms
                    "mean_ms": (lat.get("mean") or 0) / 1e6,
                    "p95_ms": (lat.get("95th") or 0) / 1e6,
                    "p99_ms": (lat.get("99th") or 0) / 1e6,
                    "max_ms": (lat.get("max") or 0) / 1e6,
                    "duration_s": (doc.get("duration") or 0) / 1e9,
                    "status_codes": doc.get("status_codes"),
                },
            )
        )
    return _inventory("vegeta", path.parent, facts, diagnostics, hashes)


def extract_wrk(path: Path) -> CodeInventory:
    """wrk stdout summary -> a `test.wrk.summary` fact.

    wrk prints text; we parse only what it printed — absent percentile
    lines (no ``--latency``) stay absent.
    """
    path = Path(path)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    text = _load_text(path, path.name, hashes, diagnostics)
    facts: list[Fact] = []
    if text is not None:
        m = re.search(r"(\d+) requests in ([\d.]+)(\w+)", text)
        rps = re.search(r"Requests/sec:\s*([\d.]+)", text)
        non2xx = re.search(r"Non-2xx or 3xx responses:\s*(\d+)", text)
        p99 = re.search(r"^\s*99%\s+([\d.]+)(\w+)", text, re.MULTILINE)
        facts.append(
            _fact(
                "test.wrk.summary",
                path.name,
                hashes[path.name],
                {
                    "requests": int(m.group(1)) if m else None,
                    "rps": float(rps.group(1)) if rps else None,
                    "non_2xx": int(non2xx.group(1)) if non2xx else 0,
                },
                {
                    "p99": (p99.group(1) + p99.group(2)) if p99 else None,
                },
            )
        )
    return _inventory("wrk", path.parent, facts, diagnostics, hashes)


def extract_hey(path: Path) -> CodeInventory:
    """hey ``-o csv`` per-request export -> a `test.hey.summary` fact."""
    path = Path(path)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    text = _load_text(path, path.name, hashes, diagnostics)
    facts: list[Fact] = []
    if text is not None:
        rows = [r for r in csv.reader(io.StringIO(text)) if r]
        times = []
        for row in rows[1:]:  # header: response-time,DNS+dialup,...
            try:
                times.append(float(row[0]) * 1000.0)  # seconds -> ms
            except (ValueError, IndexError):
                continue
        if times:
            facts.append(
                _fact(
                    "test.hey.summary",
                    path.name,
                    hashes[path.name],
                    {"requests": len(times)},
                    {
                        "avg_ms": sum(times) / len(times),
                        "p95_ms": _percentile(times, 95),
                        "p99_ms": _percentile(times, 99),
                        "max_ms": max(times),
                    },
                )
            )
    return _inventory("hey", path.parent, facts, diagnostics, hashes)


def extract_pytest_benchmark(path: Path) -> CodeInventory:
    """pytest-benchmark ``--benchmark-json`` -> one fact per benchmark.

    Microbenchmarks measure code in-process — the kind is deliberately
    distinct from a load run; RPS/TPS fields do not exist here.
    """
    path = Path(path)
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    doc = _load(path, path.name, hashes, diagnostics)
    facts: list[Fact] = []
    if isinstance(doc, dict):
        for bench in doc.get("benchmarks", []):
            if not isinstance(bench, dict):
                continue
            stats = bench.get("stats") or {}
            facts.append(
                _fact(
                    "test.pytest_benchmark.summary",
                    path.name,
                    hashes[path.name],
                    {
                        "name": bench.get("name", ""),
                        "rounds": stats.get("rounds"),
                        "mean_s": stats.get("mean"),
                        "stddev_s": stats.get("stddev"),
                    },
                    {
                        "min_s": stats.get("min"),
                        "max_s": stats.get("max"),
                        "median_s": stats.get("median"),
                    },
                )
            )
    return _inventory("pytest-benchmark", path.parent, facts, diagnostics, hashes)
