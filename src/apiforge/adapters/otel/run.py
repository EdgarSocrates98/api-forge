"""Fold otel inventory facts into the PerformanceRun contract."""

from __future__ import annotations

from typing import Any

from apiforge.adapters.inventory import CodeInventory
from apiforge.contracts.stubs import PerformanceRun
from apiforge.core.ids import stable_id


def build_performance_run(inventory: CodeInventory, input_name: str) -> PerformanceRun:
    operations: dict[str, Any] = {}
    span_count = 0
    duration_ms = 0.0
    subject = ""
    for fact in inventory.facts:
        if fact.kind == "perf.otel.operation":
            op = str(fact.measures["operation"])
            operations[op] = {
                "count": fact.measures["count"],
                "mean_ms": fact.measures["mean_ms"],
                "p95_ms": fact.measures["p95_ms"],
                "max_ms": fact.measures["max_ms"],
            }
        elif fact.kind == "perf.otel.run":
            raw_count = fact.measures.get("span_count")
            raw_dur = fact.measures.get("duration_ms")
            if isinstance(raw_count, (int, float)):
                span_count = int(raw_count)
            if isinstance(raw_dur, (int, float)):
                duration_ms = float(raw_dur)
            subject = str(fact.attrs.get("service", ""))
    unresolved = tuple(sorted({d.code for d in inventory.diagnostics}))
    return PerformanceRun(
        id=stable_id("perfrun", {"input": input_name, "service": subject}),
        produced_by="apiforge",
        subject=subject,
        duration_ms=duration_ms,
        unresolved=unresolved,
        attributes={
            "span_count": span_count,
            "operations": operations,
            "source": input_name,
        },
    )
