from __future__ import annotations

from pathlib import Path

from apiforge.application.change_control import run_change_control
from apiforge.integrations.replay import ReplayAdapter


def test_change_control_writes_governed_artifacts(tmp_path: Path) -> None:
    bundle = ReplayAdapter().load(Path("tests/fixtures/api_git_cicd/change_bundle.json"))
    result = run_change_control(bundle, tmp_path / "run")
    assert result.status == "review"
    assert result.payload["route"]["recommended_agent"] == "api-governance-reviewer"
    for name in ("result.json", "next-step.json", "graph.json", "brief.json", "metrics.json"):
        assert (tmp_path / "run" / name).is_file()
    assert (tmp_path / "run" / "evidence" / "receipt.json").is_file()
