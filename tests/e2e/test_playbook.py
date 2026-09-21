"""E2E: `apiforge playbook` renders the declared executor decomposition."""

import json

from typer.testing import CliRunner

from apiforge.cli import app

runner = CliRunner()


def test_playbook_renders_ordered_steps() -> None:
    result = runner.invoke(app, ["playbook", "api-governance-reviewer"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["coordinator"] == "api-governance-reviewer"
    verbs = [s["verb"] for s in data["steps"]]
    assert verbs == ["discover", "analyze", "judge", "evidence emit", "next-step"]
    executors = {s["executor"] for s in data["steps"]}
    assert executors <= {
        "af-inventory",
        "af-extractor",
        "af-judge",
        "af-verifier",
        "af-synthesizer",
    }


def test_playbook_unknown_coordinator_refuses() -> None:
    result = runner.invoke(app, ["playbook", "not-an-agent"])
    assert result.exit_code == 2
    assert "AF-PLAYBOOK-NOT-FOUND" in result.output


def test_playbook_covers_all_coordinator_profiles() -> None:
    from pathlib import Path

    from apiforge.rules.catalog import load_playbooks

    agents_dir = Path(__file__).resolve().parents[2] / "agents"
    profiles = {p.stem for p in agents_dir.glob("*.md")}
    assert profiles == set(load_playbooks())
