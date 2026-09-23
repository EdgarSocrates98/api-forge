from __future__ import annotations

from pathlib import Path

from apiforge.application.change_control import run_change_control
from apiforge.integrations.replay import ReplayAdapter
from apiforge.surfaces.change_control_host import render_ui_document, surface_projection


def test_ide_and_ui_projections_preserve_canonical_result(tmp_path: Path) -> None:
    bundle = ReplayAdapter().load(Path("tests/fixtures/api_git_cicd/change_bundle.json"))
    run_dir = tmp_path / "run"
    run_change_control(bundle, run_dir)
    ide = surface_projection(run_dir, "ide")
    ui = surface_projection(run_dir, "ui")
    assert ide["result"] == ui["result"]
    assert ide["result"]["status"] == "review"
    assert "CapabilityResult/v1" == ide["contract"]
    assert "API Forge change-control" in render_ui_document(run_dir)
