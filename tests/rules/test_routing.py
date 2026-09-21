import pytest

from apiforge.application.next_step import RoutingError, load_routing, next_step
from apiforge.core.models import Finding, FindingStatus, Severity


def _finding(rule_id: str, severity: Severity = Severity.MEDIUM) -> Finding:
    return Finding(
        finding_id=f"finding:{rule_id}",
        rule_id=rule_id,
        title="t",
        severity=severity,
        status=FindingStatus.CONFIRMED,
        detail="d",
        evidence=("fact:x",),
    )


def test_known_area_routes_to_declared_agent() -> None:
    step = next_step((_finding("AF-CONTRACT-001"),), phase="verify")
    assert step.recommended_agent == "api-governance-reviewer"
    assert step.dominant_area == "CONTRACT"
    assert step.finding_count == 1


def test_empty_findings_are_named() -> None:
    with pytest.raises(RoutingError, match="AF-ROUTING-NO-FINDINGS"):
        next_step((), phase="verify")


def test_phase_without_route_is_named() -> None:
    with pytest.raises(RoutingError, match="AF-ROUTING-NO-ROUTE"):
        next_step((_finding("AF-CONTRACT-001"),), phase="ship")


def test_area_tie_breaks_deterministically() -> None:
    findings = (
        _finding("AF-CODE-002", Severity.LOW),
        _finding("AF-CONTRACT-001", Severity.HIGH),
    )
    # 1-1 count tie -> the area of the highest-severity finding wins
    step = next_step(findings, phase="verify")
    assert step.dominant_area == "CONTRACT"
    again = next_step(tuple(reversed(findings)), phase="verify")
    assert again.dominant_area == step.dominant_area


def test_routing_catalog_loads() -> None:
    routes = load_routing()
    assert routes
    assert all(r.recommended_agent for r in routes)
