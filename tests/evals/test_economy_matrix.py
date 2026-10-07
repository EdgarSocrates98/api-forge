from __future__ import annotations

import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from apiforge.cli import app
from apiforge.contracts.agentic import AgentScorecard
from apiforge.contracts.base import ContractError
from apiforge.contracts.routing import CandidateAssessment
from apiforge.contracts.scorecard_routing import ScorecardRoutingPolicy
from apiforge.economy.roi import role_roi
from apiforge.evals.gate import evaluate, load_report
from apiforge.evals.matrix import load_tasks, mutate, run_matrix, verdict_for
from apiforge.evals.replay import replay
from apiforge.mcp import tools
from apiforge.runtime.adapters import FakeModelAdapter
from apiforge.runtime.information_gain import assess
from apiforge.runtime.runner import run_runtime
from apiforge.runtime.scorecard_routing import assess_scorecard_routing
from tests.runtime.economy_support import TASK_ID, economy_task

REPO = Path(__file__).resolve().parents[2]
CORPUS = REPO / "evals" / "corpus" / "economy-matrix"
runner = CliRunner()


@pytest.fixture(scope="module")
def small_report(tmp_path_factory: pytest.TempPathFactory):
    corpus = tmp_path_factory.mktemp("matrix")
    for name in ("openapi-add-operation", "openapi-remove-create-operation", "grpc-breaking-field"):
        shutil.copyfile(CORPUS / f"{name}.yaml", corpus / f"{name}.yaml")
    return run_matrix(corpus, REPO)


def test_every_task_verdict_matches_ground_truth(tmp_path: Path) -> None:
    for task in load_tasks(CORPUS):
        verdict, evidence, _ = verdict_for(task, REPO, tmp_path / str(task["id"]))
        assert verdict == task["expected"], task["id"]
        if verdict == "breaking":
            assert evidence


def test_mutants_flip_compatible_candidates(tmp_path: Path) -> None:
    task = next(t for t in load_tasks(CORPUS) if t["id"] == "openapi-add-operation")
    for kind in ("remove_operation", "remove_response_property", "add_required_request_property"):
        mutated = dict(task, candidate=mutate(task["candidate"], kind))
        assert verdict_for(mutated, REPO, tmp_path / kind)[0] == "breaking", kind
    with pytest.raises(ContractError):
        mutate(task["candidate"], "nonsense")


def test_matrix_axes_are_separate_and_gates_pass(small_report) -> None:
    assert small_report.passed, small_report.gates
    assert len(small_report.rows) == 9
    assert set(small_report.axes) == {"economy", "balanced", "deep"}
    for axes in small_report.axes.values():
        assert "quality_rate" in axes and "calls_mean" in axes and "score" not in axes
    calls = [small_report.axes[p]["calls_mean"] for p in ("economy", "balanced", "deep")]
    assert calls == sorted(calls)


def test_gate_ships_identical_and_rejects_regressions(small_report) -> None:
    same = evaluate(small_report, small_report)
    assert same.decision == "ship"
    rows = list(small_report.rows)
    broken = rows[0].model_copy(
        update={"quality": rows[0].quality.model_copy(update={"verdict_ok": False})}
    )
    unsafe = rows[1].model_copy(
        update={"quality": rows[1].quality.model_copy(update={"safety_ok": False})}
    )
    candidate = small_report.model_copy(update={"rows": (broken, unsafe, *rows[2:])})
    gate = evaluate(small_report, candidate, max_quality_regression=5)
    assert gate.decision == "reject"
    assert gate.safety_regressions and gate.quality_regressions
    with pytest.raises(ContractError) as mismatch:
        evaluate(small_report, small_report.model_copy(update={"rows": tuple(rows[1:])}))
    assert mismatch.value.code == "AF-EVALS-GATE-MISMATCH"


def test_gate_cli_and_mcp_parity(small_report, tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    report.write_text(small_report.model_dump_json(), encoding="utf-8")
    cli = runner.invoke(
        app, ["evals", "gate", "--baseline", str(report), "--candidate", str(report)]
    )
    assert cli.exit_code == 0, cli.output
    assert json.loads(cli.output) == tools.evals_gate(str(report), str(report))
    bad = tmp_path / "bad.json"
    bad.write_text("{}", encoding="utf-8")
    with pytest.raises(ContractError) as invalid:
        load_report(bad)
    assert invalid.value.code == "AF-EVALS-GATE-INVALID"


def test_replay_corpus_keeps_required_roles() -> None:
    corpus = REPO / "evals" / "corpus" / "economy-replay"
    same = replay(corpus=corpus)
    assert same.passed and same.changed == 0 and len(same.runs) == 4
    cheaper = replay(corpus=corpus, profile="economy")
    assert cheaper.passed and cheaper.removed_required_roles == 0
    assert json.loads(json.dumps(tools.evals_replay(corpus=str(corpus)))) == json.loads(
        same.model_dump_json()
    )


def test_replay_marks_incomplete_runs_unresolved(tmp_path: Path) -> None:
    (tmp_path / "broken.json").write_text(json.dumps({"task_id": "x"}), encoding="utf-8")
    report = replay(corpus=tmp_path)
    assert report.unresolved == 1 and report.runs[0].reason.startswith("AF-REPLAY-RUN-INCOMPLETE")


def test_information_gain_levels() -> None:
    def artifact(recommendation: str, confidence: float, unresolved=()):
        return SimpleNamespace(
            payload={"recommendation": recommendation},
            confidence=confidence,
            unresolved=tuple(unresolved),
        )

    assert assess([artifact("ship", 0.9), artifact("ship", 0.8)]).level == "low"
    assert assess([artifact("ship", 0.9), artifact("block", 0.9)]).level == "high"
    assert assess([artifact("ship", 0.9, ["gap"])]).level == "high"
    assert assess([artifact("ship", 0.5)]).level == "medium"


def test_runtime_reports_information_gain_and_roi(tmp_path: Path) -> None:
    economy_task(tmp_path)
    result = run_runtime(
        tmp_path, TASK_ID, adapter=FakeModelAdapter(), now="2026-09-28T00:00:00+00:00"
    )
    assert result["economy"]["information_gain"]["level"] in {"low", "medium", "high"}
    roi = role_roi(tmp_path)
    assert roi["runs"] == 1
    assert all(row["calls"] >= 1 for row in roi["roles"])
    assert tools.economy_roi(str(tmp_path)) == roi


def _candidate(name: str) -> CandidateAssessment:
    return CandidateAssessment(capability=name, agent=f"{name}-agent", eligible=True)


def _card(name: str, quality: float, cost: float) -> AgentScorecard:
    return AgentScorecard(
        agent=f"{name}-agent",
        profile_id=name,
        evaluation_count=10,
        passed_count=10,
        quality_score=quality,
        quality_promoted=True,
        observed_cost=cost,
        freshness_state="fresh",
    )


def test_quality_floor_is_a_constraint_and_cost_the_optimization() -> None:
    candidates = [_candidate("A"), _candidate("B"), _candidate("C")]
    cards = {"A": _card("A", 0.98, 10), "B": _card("B", 0.96, 3), "C": _card("C", 0.70, 1)}
    floored = assess_scorecard_routing(
        candidates, cards, ScorecardRoutingPolicy(quality_floor=0.95, challenger_slots=0)
    )
    assert floored.champion_order == ("B", "A")
    assert floored.unresolved_order == ("C",)
    reasons = {item.candidate: item.reason_codes for item in floored.candidates}
    assert reasons["C"] == ("quality-below-floor",)
    default = assess_scorecard_routing(candidates, cards, ScorecardRoutingPolicy())
    assert default.champion_order == ("A", "B", "C")
