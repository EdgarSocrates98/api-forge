"""OTLP/JSON trace export -> perf.otel.* facts.

Reads a collector-style ``{"resourceSpans": [...]}`` document. Spans are
aggregated per *operation*: ``METHOD route`` when the ``http.route`` (or
``url.path``) attribute is present, else the span name. Statistics are
nearest-rank percentiles over span durations — deterministic given the
same export. Spans without usable timestamps are counted and named in a
diagnostic, never silently dropped; a missing ``service.name`` leaves the
run's subject unresolved rather than guessed.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from apiforge.adapters.inventory import CodeInventory
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_EXTRACTOR = "otel"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _diag(path: Path, digest: str, code: str, message: str) -> Diagnostic:
    return Diagnostic(
        code=code,
        status=FindingStatus.UNRESOLVED,
        message=message,
        source=SourceRef(path=path.name, sha256=digest, extractor=_EXTRACTOR),
    )


def _attr_value(entry: object) -> str | None:
    if not isinstance(entry, dict):
        return None
    value = entry.get("value")
    if isinstance(value, dict):
        for key in ("stringValue", "intValue", "doubleValue", "boolValue"):
            if key in value:
                return str(value[key])
    return None


def _attrs(span: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for entry in span.get("attributes") or []:
        if isinstance(entry, dict) and isinstance(entry.get("key"), str):
            val = _attr_value(entry)
            if val is not None:
                out[entry["key"]] = val
    return out


def _operation(span: dict[str, Any]) -> str:
    attrs = _attrs(span)
    route = attrs.get("http.route") or attrs.get("url.path")
    method = attrs.get("http.request.method") or attrs.get("http.method")
    if route and method:
        return f"{method} {route}"
    if route:
        return str(route)
    name = span.get("name")
    return str(name) if name else "unnamed"


def _percentile(sorted_ms: list[float], pct: float) -> float:
    """Nearest-rank percentile over sorted values."""
    index = max(0, math.ceil(pct * len(sorted_ms)) - 1)
    return sorted_ms[index]


def _service_name(doc: dict[str, Any]) -> str | None:
    for rs in doc.get("resourceSpans") or []:
        if not isinstance(rs, dict):
            continue
        resource = rs.get("resource") or {}
        for entry in resource.get("attributes") or []:
            if isinstance(entry, dict) and entry.get("key") == "service.name":
                return _attr_value(entry)
    return None


def extract_otel(path: Path) -> CodeInventory:
    """One OTLP/JSON export -> perf.otel.run + perf.otel.operation facts."""
    path = Path(path)
    digest = _digest(path) if path.is_file() else "0" * 64
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return CodeInventory(
            framework="otel",
            root=str(path.parent),
            diagnostics=(_diag(path, digest, "AF-OTEL-REPORT-INVALID", str(exc)),),
            input_hashes={path.name: digest},
        )
    if not isinstance(doc, dict) or not isinstance(doc.get("resourceSpans"), list):
        return CodeInventory(
            framework="otel",
            root=str(path.parent),
            diagnostics=(_diag(path, digest, "AF-OTEL-REPORT-INVALID", "missing resourceSpans"),),
            input_hashes={path.name: digest},
        )
    diagnostics: list[Diagnostic] = []
    durations: dict[str, list[float]] = {}
    incomplete = 0
    span_count = 0
    error_spans = 0
    t_min: int | None = None
    t_max: int | None = None
    for rs in doc["resourceSpans"]:
        if not isinstance(rs, dict):
            continue
        for ss in rs.get("scopeSpans") or []:
            if not isinstance(ss, dict):
                continue
            for span in ss.get("spans") or []:
                if not isinstance(span, dict):
                    continue
                span_count += 1
                start, end = span.get("startTimeUnixNano"), span.get("endTimeUnixNano")
                if not isinstance(start, int) or not isinstance(end, int) or end < start:
                    incomplete += 1
                    continue
                status = span.get("status") or {}
                if str(status.get("code", "")).upper() == "STATUS_CODE_ERROR":
                    error_spans += 1
                t_min = start if t_min is None else min(t_min, start)
                t_max = end if t_max is None else max(t_max, end)
                durations.setdefault(_operation(span), []).append((end - start) / 1_000_000.0)
    if incomplete:
        diagnostics.append(
            _diag(
                path,
                digest,
                "AF-OTEL-SPAN-INCOMPLETE",
                f"{incomplete} of {span_count} spans lack usable timestamps",
            )
        )
    if _service_name(doc) is None:
        diagnostics.append(
            _diag(
                path,
                digest,
                "AF-OTEL-SERVICE-UNKNOWN",
                "no resource attribute service.name",
            )
        )
    facts: list[Fact] = [
        Fact(
            fact_id=stable_id("fact", {"kind": "perf.otel.run", "file": path.name}),
            kind="perf.otel.run",
            source=SourceRef(path=path.name, sha256=digest, extractor=_EXTRACTOR),
            measures={
                "span_count": span_count,
                "duration_ms": (
                    (t_max - t_min) / 1_000_000.0
                    if t_min is not None and t_max is not None
                    else 0.0
                ),
                "error_spans": error_spans,
            },
            attrs={"service": _service_name(doc) or "unknown"},
        )
    ]
    for operation in sorted(durations):
        series = sorted(durations[operation])
        facts.append(
            Fact(
                fact_id=stable_id(
                    "fact",
                    {"kind": "perf.otel.operation", "file": path.name, "op": operation},
                ),
                kind="perf.otel.operation",
                source=SourceRef(path=path.name, sha256=digest, extractor=_EXTRACTOR),
                measures={
                    "operation": operation,
                    "count": len(series),
                    "mean_ms": sum(series) / len(series),
                    "p95_ms": _percentile(series, 0.95),
                    "max_ms": series[-1],
                },
                attrs={},
            )
        )
    return CodeInventory(
        framework="otel",
        root=str(path.parent),
        facts=tuple(facts),
        diagnostics=tuple(diagnostics),
        input_hashes={path.name: digest},
    )
