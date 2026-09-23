from __future__ import annotations

from pathlib import Path

from apiforge.application.change_control import (
    build_change_collection_receipt,
    run_change_control,
)
from apiforge.application.change_publishers import (
    publish_change_control_reports,
    render_junit,
    render_markdown,
)
from apiforge.contracts.change_control import ChangeCollectRequest
from apiforge.core.io import write_json
from apiforge.integrations.github import GitHubReadOnlyAdapter
from apiforge.integrations.replay import ReplayAdapter


def test_change_control_writes_governed_artifacts(tmp_path: Path) -> None:
    bundle = ReplayAdapter().load(Path("tests/fixtures/api_git_cicd/change_bundle.json"))
    result = run_change_control(bundle, tmp_path / "run")
    assert result.status == "review"
    assert result.payload["route"]["recommended_agent"] == "api-governance-reviewer"
    for name in ("result.json", "next-step.json", "graph.json", "brief.json", "metrics.json"):
        assert (tmp_path / "run" / name).is_file()
    assert (tmp_path / "run" / "evidence" / "receipt.json").is_file()


def test_change_control_publishers_emit_junit_and_markdown(tmp_path: Path) -> None:
    bundle = ReplayAdapter().load(Path("tests/fixtures/api_git_cicd/change_bundle.json"))
    run_dir = tmp_path / "run"
    result = run_change_control(bundle, run_dir)
    reports = publish_change_control_reports(run_dir)
    assert "<testsuite" in Path(reports["junit"]).read_text(encoding="utf-8")
    markdown = Path(reports["markdown"]).read_text(encoding="utf-8")
    assert "# API Forge change-control report" in markdown
    assert "review" in markdown
    assert "<testsuite" in render_junit(result)
    assert "Recommendation" in render_markdown(result)


def test_live_collection_receipt_binds_sanitized_bundle(tmp_path: Path) -> None:
    class Transport:
        def get_json(self, path: str, *, params=None) -> object:
            if path.endswith("check-runs"):
                return {"check_runs": [{"name": "ci", "conclusion": "success"}]}
            return {"files": [], "ahead_by": 1, "behind_by": 0}

    bundle = GitHubReadOnlyAdapter(Transport()).collect(
        ChangeCollectRequest(
            repository="example/repo",
            base_sha="0" * 40,
            head_sha="1" * 40,
        )
    )
    bundle_path = tmp_path / "bundle.json"
    write_json(bundle_path, bundle)
    receipt = build_change_collection_receipt(bundle, bundle_path)
    assert receipt.schema_version == "af-change-collection-receipt/1"
    assert receipt.read_only is True
    assert receipt.mutation_allowed is False
    assert receipt.check_conclusions == ("success",)
