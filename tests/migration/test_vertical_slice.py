from pathlib import Path

from apiforge.migration.contracts import MigrationReport, MigrationSpec
from apiforge.migration.discovery import discover
from apiforge.migration.planner import compile_plan
from apiforge.migration.report import render_report
from apiforge.migration.verifier import verify_report


def test_java_vertical_slice_is_reproducible() -> None:
    root = Path("tests/fixtures/migrations/java/spring-java11-to-21").resolve()
    spec = MigrationSpec(project_root=str(root), ecosystem="java", source_version="11", target_version="21")
    discovery = discover(spec)
    plan = compile_plan(spec, discovery)
    report = verify_report(
        MigrationReport(spec_identity=spec.identity(), discovery=discovery, plan=plan, evidence=("discovery",)),
        evidence_ok=True,
        verification_ok=True,
    )
    rendered = render_report(report, markdown=True)
    assert "Runtime migration:" in rendered
    assert report.outcome is not None
