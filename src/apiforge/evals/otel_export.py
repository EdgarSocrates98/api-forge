"""§50-§52 deterministic evals: span ledger -> OTLP export -> acceptance."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.runtime.agent_telemetry import append_span, build_span
from apiforge.runtime.otel_export import export_otlp, validate_otlp


def load_cases(corpus: Path) -> list[dict[str, Any]]:
    cases = [
        yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(Path(corpus).glob("*.yaml"))
    ]
    ids = [case.get("id") for case in cases]
    if not cases or len(ids) != len(set(ids)):
        raise ContractError("AF-EVALS-INVALID", f"otel-export corpus {corpus} empty or duplicated")
    return cases


def _run_case(case: dict[str, Any], root: Path) -> dict[str, Any]:
    failures: list[str] = []
    for row in case.get("spans") or ():
        span = build_span(
            trace_id=row.get("trace_id", "trace-eval"),
            task_id=row.get("task_id", "task-eval"),
            run_id=row.get("run_id", "run-eval"),
            operation=row["operation"],
            started_at=row.get("started_at", "2026-10-06T10:00:00Z"),
            ended_at=row.get("ended_at"),
            status=row.get("status", "ok"),
            agent_name=row.get("agent_name"),
            tool_name=row.get("tool_name"),
            decision_id=row.get("decision_id"),
            memory_id=row.get("memory_id"),
            context_id=row.get("context_id"),
            unresolved=tuple(row.get("unresolved") or ()),
        )
        append_span(root, span)
    export = export_otlp(root)
    validation = validate_otlp(export.payload)
    expect = case.get("expect") or {}
    if "accepted" in expect and validation.accepted != expect["accepted"]:
        failures.append(f"accepted {validation.accepted} != {expect['accepted']}")
    if "span_count" in expect and export.span_count != expect["span_count"]:
        failures.append(f"span_count {export.span_count} != {expect['span_count']}")
    wanted_ops = set(expect.get("operations") or ())
    if wanted_ops and set(validation.operations) != wanted_ops:
        failures.append(f"operations {sorted(validation.operations)} != {sorted(wanted_ops)}")
    if "export_unresolved" in expect:
        missing = [
            item
            for item in expect["export_unresolved"]
            if not any(item in entry for entry in export.unresolved)
        ]
        if missing:
            failures.append(f"export unresolved missing {missing}")
    if "traceparent" in expect:
        from apiforge.runtime.otel_export import parse_traceparent

        tp = expect["traceparent"]
        try:
            parse_traceparent(tp)
            ok = True
        except ContractError:
            ok = False
        if not ok:
            failures.append(f"traceparent {tp!r} refused")
    return {"id": case["id"], "passed": not failures, "failures": failures}


def run_otel_export(corpus: Path) -> dict[str, Any]:
    cases = load_cases(corpus)
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="af-otel-evals-") as tmp:
        for index, case in enumerate(cases):
            results.append(_run_case(case, Path(tmp) / str(index)))
    failed = [result["id"] for result in results if not result["passed"]]
    return {
        "schema": "apiforge/otel-export-evals/v1",
        "corpus": str(corpus),
        "cases": results,
        "totals": {"cases": len(results), "failed": len(failed), "failed_ids": failed},
        "passed": not failed,
    }


__all__ = ["load_cases", "run_otel_export"]
