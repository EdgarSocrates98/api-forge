"""perf suggest — ActionPlan from findings; never applies (AT-003)."""

import json
from pathlib import Path

from apiforge.contracts.core import ActionPlan
from apiforge.core.models import Finding
from apiforge.perf.suggest import suggest_fix

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
PROJECT = FIXTURES / "resilience_app"


def _finding(rule_id: str, status: str = "confirmed") -> Finding:
    return Finding.model_validate(
        {
            "finding_id": f"F-{rule_id}",
            "rule_id": rule_id,
            "status": status,
            "severity": "high",
            "title": "x",
            "evidence": ["fact-1"] if status == "confirmed" else [],
        }
    )


def test_confirmed_findings_become_remediate_steps() -> None:
    plan = suggest_fix([_finding("AF-PERF-101"), _finding("AF-PERF-104")])
    ActionPlan.model_validate(plan.model_dump(mode="json"))
    assert plan.status == "proposed"
    assert plan.requires_approval is True
    assert len(plan.steps) == 2
    step = plan.steps[0]
    assert step.verb == "remediate"  # absent from dispatch — can never run
    assert step.args["rule_id"] == "AF-PERF-101"
    assert step.args["intent"]  # catalog remediation text
    assert list(step.args["evidence"]) == ["fact-1"]


def test_unconfirmed_and_unmapped_findings_named() -> None:
    plan = suggest_fix(
        [_finding("AF-PERF-101", status="unresolved"), _finding("AF-UNKNOWN-1")]
    )
    assert plan.steps == ()
    assert "AF-UNKNOWN-1" in plan.reason
    assert "unresolved" in plan.reason


def test_empty_findings_named() -> None:
    plan = suggest_fix([])
    assert plan.steps == ()
    assert plan.reason == "no findings supplied"


def test_suggest_never_writes(tmp_path: Path) -> None:
    """AT-003: suggest over a case dir leaves the project bytes unchanged."""
    from apiforge.adapters.resilience import extract_resilience
    from apiforge.rules.fact_judge import judge_facts

    before = {
        p: p.read_bytes() for p in sorted(PROJECT.rglob("*")) if p.is_file()
    }
    inventory = extract_resilience(PROJECT)
    findings = judge_facts(inventory.facts)
    plan = suggest_fix(findings)
    assert json.dumps(plan.model_dump(mode="json"))
    after = {
        p: p.read_bytes() for p in sorted(PROJECT.rglob("*")) if p.is_file()
    }
    assert before == after
