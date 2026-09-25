from pathlib import Path

import yaml

from apiforge.contracts.routing_evolution import EvolutionPolicy
from apiforge.runtime.runner import run_runtime
from tests.runtime.test_runtime import make_task


def test_wave_zero_fixture_covers_golden_holdout_and_mutation_shapes() -> None:
    fixture = yaml.safe_load(
        Path("tests/fixtures/agentic_runtime/evolution_cases.yaml").read_text(encoding="utf-8")
    )
    assert {item["kind"] for item in fixture["cases"]} == {"golden", "holdout", "mutation"}
    assert {item["mode"] for item in fixture["cases"]} == {
        "local",
        "replay",
        "shadow",
        "external-read",
    }


def test_local_supervisor_persists_active_evolution_gate(tmp_path: Path) -> None:
    make_task(tmp_path)
    result = run_runtime(tmp_path, "evolve-orders-api", now="2026-09-24T12:00:00+00:00")
    evolution = Path(str(result["run_dir"])) / "evolution.json"
    assert evolution.is_file()
    payload = yaml.safe_load(evolution.read_text(encoding="utf-8"))
    assert payload["mode"] == "local"
    assert payload["state"] == "active"
    assert payload["coverage"]["state"] == "complete"


def test_shadow_policy_stops_before_capability_invocation(tmp_path: Path, monkeypatch) -> None:
    make_task(tmp_path)
    monkeypatch.setattr(
        "apiforge.runtime.supervisor.load_evolution_policy",
        lambda: EvolutionPolicy(mode="shadow"),
    )
    result = run_runtime(tmp_path, "evolve-orders-api", now="2026-09-24T12:00:00+00:00")
    assert result["status"] == "REVIEW"
    assert result["artifacts"] == []
    assert "evolution" in result
