"""Deterministic routing: findings + phase -> recommended agent.

The route table is data (`rules/catalog/routing.yaml`); nobody picks a
coordinator by inspection. No route means a named refusal, never a guess.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from importlib import resources
from typing import Any

from pydantic import BaseModel, ConfigDict

from apiforge.core.models import Finding, Severity
from apiforge.core.yaml import StrictLoadError, load_yaml_strict
from apiforge.rules.catalog import CatalogError, load_catalog


class RoutingError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


class Route(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    phase: str
    dominant_area: str
    recommended_agent: str
    rationale: str = ""


class NextStep(BaseModel):
    model_config = ConfigDict(frozen=True)

    recommended_agent: str
    dominant_area: str
    phase: str
    finding_count: int
    unmapped_count: int
    rationale: str


_SEVERITY_RANK = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
    Severity.INFO: 4,
}


def load_routing() -> tuple[Route, ...]:
    text = (
        resources.files("apiforge.rules")
        .joinpath("catalog/routing.yaml")
        .read_text(encoding="utf-8")
    )
    try:
        data: Any = load_yaml_strict(text, source="apiforge.rules routing")
    except StrictLoadError as exc:
        raise RoutingError("AF-ROUTING-SCHEMA", str(exc)) from exc
    if not isinstance(data, Mapping) or not isinstance(data.get("routes"), list):
        raise RoutingError("AF-ROUTING-SCHEMA", "missing 'routes' list")
    routes: list[Route] = []
    for index, entry in enumerate(data["routes"]):
        try:
            routes.append(Route.model_validate(entry))
        except Exception as exc:
            raise RoutingError("AF-ROUTING-SCHEMA", f"routes[{index}] invalid: {exc}") from exc
    return tuple(routes)


def _dominant_area(counts: Counter[str], best_severity: dict[str, int]) -> str:
    top = max(counts.values())
    tied = [a for a, c in counts.items() if c == top]
    if len(tied) == 1:
        return tied[0]
    return min(tied, key=lambda a: (best_severity[a], a))


def next_step(
    findings: tuple[Finding, ...],
    phase: str,
    *,
    catalog: dict[str, Any] | None = None,
    routes: tuple[Route, ...] | None = None,
) -> NextStep:
    """Compose over findings — reads no artifact."""
    if not findings:
        raise RoutingError("AF-ROUTING-NO-FINDINGS", "no findings to route on")
    try:
        meta = catalog if catalog is not None else load_catalog()
    except CatalogError as exc:
        raise RoutingError("AF-ROUTING-CATALOG", str(exc)) from exc
    counts: Counter[str] = Counter()
    best: dict[str, int] = {}
    unmapped = 0
    for finding in findings:
        rule = meta.get(finding.rule_id)
        if rule is None:
            unmapped += 1
            continue
        counts[rule.area] += 1
        rank = _SEVERITY_RANK[finding.severity]
        best[rule.area] = min(best.get(rule.area, 99), rank)
    if not counts:
        raise RoutingError(
            "AF-ROUTING-NO-ROUTE",
            "no finding maps to a catalog area",
        )
    dominant = _dominant_area(counts, best)
    table = routes if routes is not None else load_routing()
    for route in table:
        if route.phase == phase and route.dominant_area == dominant:
            return NextStep(
                recommended_agent=route.recommended_agent,
                dominant_area=dominant,
                phase=phase,
                finding_count=len(findings),
                unmapped_count=unmapped,
                rationale=route.rationale,
            )
    raise RoutingError(
        "AF-ROUTING-NO-ROUTE",
        f"no route for phase {phase!r} with dominant area {dominant!r}",
    )
