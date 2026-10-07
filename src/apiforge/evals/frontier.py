"""§23 quality × cost × latency frontier over a recorded agentic-quality
report. Quality is observed from the report's accuracy; latency is read
from optional measured durations; cost stays ``unresolved`` unless
provider-accounted data is supplied — it is never inferred.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.eval_plane import FrontierPoint, QualityFrontier


def _dominates(a: FrontierPoint, b: FrontierPoint) -> bool:
    """Pareto dominance on the observed axes: quality higher, latency
    and cost lower — axes without observed values are skipped."""
    better = False
    if a.quality is not None and b.quality is not None:
        if a.quality < b.quality:
            return False
        better = better or a.quality > b.quality
    if a.latency_ms is not None and b.latency_ms is not None:
        if a.latency_ms > b.latency_ms:
            return False
        better = better or a.latency_ms < b.latency_ms
    if a.cost is not None and b.cost is not None:
        if a.cost > b.cost:
            return False
        better = better or a.cost < b.cost
    return better


def build_frontier(
    report: dict[str, Any],
    *,
    latencies_ms: dict[str, float] | None = None,
    costs: dict[str, float] | None = None,
    source: str = "",
) -> QualityFrontier:
    accuracy = report.get("accuracy") or {}
    if not accuracy:
        raise ContractError("AF-EVALS-FRONTIER", "report carries no per-profile accuracy map")
    latencies_ms = latencies_ms or {}
    costs = costs or {}
    unresolved: list[str] = []
    points: list[FrontierPoint] = []
    for profile in sorted(accuracy):
        latency = latencies_ms.get(profile)
        cost = costs.get(profile)
        detail = ""
        if latency is None:
            unresolved.append(f"{profile}: latency not measured in source report")
            detail = "latency unmeasured"
        if cost is None:
            unresolved.append(f"{profile}: cost unresolved — no provider-accounted data supplied")
        points.append(
            FrontierPoint(
                profile=str(profile),
                quality=float(accuracy[profile]),
                latency_ms=latency,
                cost=cost,
                cost_state="observed" if cost is not None else "unresolved",
                detail=detail,
            )
        )
    points = [
        point.model_copy(
            update={
                "pareto": not any(
                    other.profile != point.profile and _dominates(other, point) for other in points
                )
            }
        )
        for point in points
    ]
    return QualityFrontier(
        points=tuple(points),
        pareto_profiles=tuple(point.profile for point in points if point.pareto),
        source=source,
        unresolved=tuple(unresolved),
    )


def run_frontier(
    report_path: Path,
    *,
    latencies: Path | None = None,
    costs: Path | None = None,
) -> dict[str, Any]:
    report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    if not isinstance(report, dict) or "accuracy" not in report:
        raise ContractError(
            "AF-EVALS-FRONTIER",
            f"{report_path}: expected an agentic-quality report with an accuracy map",
        )
    lat_map: dict[str, float] | None = None
    if latencies is not None:
        raw_lat = yaml.safe_load(Path(latencies).read_text(encoding="utf-8")) or {}
        lat_map = {str(k): float(v) for k, v in (raw_lat.get("latency_ms") or {}).items()}
    cost_map: dict[str, float] | None = None
    if costs is not None:
        raw_cost = yaml.safe_load(Path(costs).read_text(encoding="utf-8")) or {}
        cost_map = {str(k): float(v) for k, v in (raw_cost.get("cost") or {}).items()}
    frontier = build_frontier(report, latencies_ms=lat_map, costs=cost_map, source=str(report_path))
    return {
        "schema": "apiforge/quality-frontier-evals/v1",
        "report": frontier.model_dump(mode="json"),
        "totals": {
            "profiles": len(frontier.points),
            "pareto": len(frontier.pareto_profiles),
            "unresolved": len(frontier.unresolved),
        },
        "passed": True,
    }


__all__ = ["build_frontier", "run_frontier"]
