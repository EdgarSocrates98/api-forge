import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from apiforge.cli import app
from apiforge.contracts.task import TaskRisk, TaskSize
from apiforge.runtime.adapters import FakeModelAdapter
from apiforge.runtime.runner import run_runtime
from tests.runtime.economy_support import TASK_ID, economy_task, record_deterministic_run

NOW = "2026-09-23T12:32:00+00:00"
runner = CliRunner()


def _run(root: Path, profile: str | None = None, responses=None, enabled: bool = True):
    return run_runtime(
        root,
        TASK_ID,
        adapter=FakeModelAdapter(responses or {}),
        now=NOW,
        profile=profile,
        economy_enabled=enabled,
    )


def _plan(result) -> dict:
    return json.loads((Path(str(result["run_dir"])) / "routing-plan.json").read_text("utf-8"))


def test_default_profile_is_balanced(tmp_path: Path) -> None:
    economy_task(tmp_path)
    economy = _run(tmp_path)["economy"]
    assert economy["requested"] == "balanced"
    assert economy["requested_source"] == "policy"
    assert economy["effective"] == "balanced"


def test_economy_keeps_required_reviewer_and_cuts_optional_capacity(tmp_path: Path) -> None:
    economy_task(tmp_path)
    baseline = _run(tmp_path, enabled=False)
    economy_task(tmp_path / "eco")
    cheap = _run(tmp_path / "eco", "economy")
    assert _plan(cheap)["reviewers"] == _plan(baseline)["reviewers"] == ["task-review"]
    assert len(cheap["run"]["invocation_ids"]) < len(baseline["run"]["invocation_ids"])
    assert _plan(cheap)["parallel"] == []
    assert cheap["economy"]["trimmed_roles"]


def test_sensitive_request_for_economy_escalates(tmp_path: Path) -> None:
    economy_task(tmp_path, risk=TaskRisk.SENSITIVE)
    result = _run(tmp_path, "economy")
    economy = result["economy"]
    assert economy["effective"] == "balanced"
    assert "risk=sensitive" in economy["escalation_reason"]
    assert "AF-ECONOMY-ESCALATED" in economy["codes"]
    assert _plan(result)["critic"] == "adversarial-critic"


def test_task_budget_caps_calls_and_reports_exhaustion(tmp_path: Path) -> None:
    economy_task(tmp_path, max_calls=2)
    result = _run(tmp_path, "deep")
    economy = result["economy"]
    assert economy["max_calls"] == 2
    assert economy["calls_used"] <= 2
    assert economy["status"] == "unresolved"
    assert "AF-BUDGET-EXHAUSTED" in economy["codes"]
    assert any(gap.startswith("AF-BUDGET-EXHAUSTED") for gap in result["run"]["gaps"])
    assert result["status"] == "REVIEW"


def test_deterministic_proof_stops_before_any_agent_call(tmp_path: Path) -> None:
    economy_task(tmp_path)
    record_deterministic_run(tmp_path, output="specialist artifact")
    result = _run(tmp_path, "deep")
    assert result["economy"]["stopped_at"] == "L0"
    assert result["run"]["invocation_ids"] == []
    assert result["status"] == "REVIEW"
    assert result["run"]["final_status"] != "ACCEPTED"


def test_low_confidence_escalates_to_reserved_review(tmp_path: Path, monkeypatch) -> None:
    from apiforge.runtime import supervisor

    original = supervisor.build_routing_plan

    def without_reviewer(*args, **kwargs):
        return original(*args, **kwargs).model_copy(update={"reviewers": (), "required_roles": ()})

    monkeypatch.setattr(supervisor, "build_routing_plan", without_reviewer)
    economy_task(tmp_path, size=TaskSize.S)
    result = _run(
        tmp_path,
        "balanced",
        responses={"api-architecture-review": {"confidence": 0.3, "recommendation": "hold"}},
    )
    levels = [step["level"] for step in result["economy"]["ladder"]]
    assert "L3" in levels
    assert result["economy"]["reserve_left_at_verification"] >= result["economy"]["reserve_calls"]
    assert any(item["capability"] == "task-review" for item in result["artifacts"])


def test_economy_ceiling_blocks_debate_without_downgrade(tmp_path: Path) -> None:
    economy_task(tmp_path)
    result = _run(
        tmp_path,
        "economy",
        responses={"api-architecture-review": {"recommendation": "keep", "confidence": 0.9}},
    )
    economy = result["economy"]
    assert result["debate"]["opened"] is False
    assert economy["status"] == "unresolved"
    assert "AF-ECONOMY-CEILING" in economy["codes"]


def test_balanced_allows_bounded_debate(tmp_path: Path) -> None:
    economy_task(tmp_path)
    result = _run(tmp_path, "balanced")
    assert result["debate"]["opened"] is True
    assert result["debate"]["max_rounds"] == 1


def test_cli_profile_flag_and_invalid_profile(tmp_path: Path) -> None:
    economy_task(tmp_path)
    ok = runner.invoke(
        app,
        ["runtime", "run", TASK_ID, "--root", str(tmp_path), "--profile", "economy", "--now", NOW],
    )
    assert ok.exit_code == 0, ok.output
    assert json.loads(ok.output)["economy"]["requested_source"] == "flag"
    bad = runner.invoke(
        app, ["runtime", "run", TASK_ID, "--root", str(tmp_path), "--profile", "cheap"]
    )
    assert bad.exit_code == 2
    assert "AF-ECONOMY-PROFILE-INVALID" in bad.output
    assert "field=profile" in bad.output


@pytest.mark.parametrize("profile", ["economy", "balanced", "deep"])
def test_resume_accepts_profile(tmp_path: Path, profile: str) -> None:
    from apiforge.runtime.runner import resume_runtime

    economy_task(tmp_path)
    _run(tmp_path, profile)
    resumed = resume_runtime(tmp_path, TASK_ID, profile=profile)
    assert resumed["resumed"] is True
