from pathlib import Path

from apiforge.contracts.task import BriefStatus
from apiforge.migration.contracts import MigrationReport, MigrationSpec
from apiforge.migration.discovery import discover
from apiforge.migration.planner import compile_plan
from apiforge.migration.verifier import verify_report


def test_plan_has_dependency_dag_and_conservative_status() -> None:
    root = Path("tests/fixtures/migrations/go/go121-to-124").resolve()
    spec = MigrationSpec(
        project_root=str(root), ecosystem="go", source_version="1.21", target_version="1.24"
    )
    discovery = discover(spec)
    plan = compile_plan(spec, discovery)
    report = verify_report(
        MigrationReport(spec_identity=spec.identity(), discovery=discovery, plan=plan)
    )
    assert plan.task.strategy.value == "plan-execute-verify"
    assert plan.readiness is not None
    assert plan.readiness.direction == "upgrade"
    assert report.outcome is not None
    assert report.outcome.status is BriefStatus.REVIEW


def test_blocking_finding_cannot_be_done() -> None:
    root = Path("tests/fixtures/migrations/python/python2-to-3").resolve()
    spec = MigrationSpec(
        project_root=str(root), ecosystem="python", source_version="2", target_version="3"
    )
    discovery = discover(spec)
    plan = compile_plan(spec, discovery)
    report = verify_report(
        MigrationReport(spec_identity=spec.identity(), discovery=discovery, plan=plan),
        evidence_ok=True,
        verification_ok=True,
    )
    assert report.outcome is not None
    assert report.outcome.status is BriefStatus.BLOCKED
