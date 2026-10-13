from pathlib import Path

import pytest

from apiforge.contracts.base import ContractError
from apiforge.contracts.eval_plane import (
    FrontierPoint,
    LiveEvalReport,
    TraceGradeDimension,
)
from apiforge.evals.frontier import build_frontier
from apiforge.evals.live_evals import load_layer, run_live_evals
from apiforge.evals.memory_evals import run_memory_evals
from apiforge.evals.security_adversarial import run_security_adversarial
from apiforge.evals.trace_grading import grade_trace, load_rubric, run_trace_grading
from apiforge.runtime.agent_telemetry import build_span

CORPUS = Path(__file__).resolve().parents[2] / "evals" / "corpus"
RUBRIC = Path(__file__).resolve().parents[2] / "src" / "apiforge" / "rules" / "trace_rubric.yaml"
LAYER = Path(__file__).resolve().parents[2] / "src" / "apiforge" / "rules" / "live_evals.yaml"


def _span(**over) -> dict:
    base = {
        "operation": "execute_tool",
        "started_at": "2026-10-06T00:00:00Z",
        "status": "ok",
        "evidence_refs": ["ctx://e1"],
    }
    base.update(over)
    return base


def test_rubric_loads() -> None:
    rubric = load_rubric(RUBRIC)
    assert rubric["rubric_id"] == "agentic-trace/v1"
    assert len(rubric["dimensions"]) == 5


def test_grade_clean_trace_passes() -> None:
    rubric = load_rubric(RUBRIC)
    spans = [
        build_span(trace_id="t", task_id="k", run_id="r", **_span(operation="invoke_agent")),
        build_span(
            trace_id="t",
            task_id="k",
            run_id="r",
            **_span(operation="invoke_model", evidence_refs=[]),
        ),
        build_span(trace_id="t", task_id="k", run_id="r", **_span()),
    ]
    grade = grade_trace(spans, rubric)
    assert grade.verdict == "pass"
    assert grade.score is not None and grade.score >= 0.8


def test_empty_trace_is_unresolved_not_zero() -> None:
    rubric = load_rubric(RUBRIC)
    grade = grade_trace([], rubric)
    assert grade.verdict == "unresolved"
    assert grade.score is None


def test_error_span_without_message_drops_honesty() -> None:
    rubric = load_rubric(RUBRIC)
    spans = [
        build_span(trace_id="t", task_id="k", run_id="r", **_span(status="error")),
        build_span(
            trace_id="t",
            task_id="k",
            run_id="r",
            **_span(operation="invoke_model", evidence_refs=[]),
        ),
    ]
    grade = grade_trace(spans, rubric)
    honesty = next(d for d in grade.dimensions if d.dimension == "status_honesty")
    assert honesty.score == 0.0


def test_trace_grading_corpus_green() -> None:
    result = run_trace_grading(CORPUS / "trace-grading")
    assert result["passed"], result["cases"]
    assert result["totals"]["cases"] == 5


def test_unresolved_dimension_requires_reason() -> None:
    with pytest.raises(ValueError):
        TraceGradeDimension(dimension="x", weight=0.5, state="unresolved")


def test_adversarial_corpus_all_contained_or_refused() -> None:
    result = run_security_adversarial(CORPUS / "security-adversarial")
    assert result["passed"], [c for c in result["cases"] if not c["passed"]]
    assert result["totals"]["escaped"] == 0
    assert result["totals"]["cases"] == 16


def test_memory_corpus_covers_axes() -> None:
    result = run_memory_evals(CORPUS / "memory-evals")
    assert result["passed"], [c for c in result["cases"] if not c["passed"]]
    axes = {c["axis"] for c in result["cases"]}
    assert "memory_poisoning" in axes
    assert "cross_task_leakage" in axes


def test_layer_loads_and_defers_provider() -> None:
    layer = load_layer(LAYER)
    assert layer.provider_tier == "deferred_external"
    assert len(layer.deterministic_evals) == 4


def test_live_report_defers_provider_honestly() -> None:
    result = run_live_evals(LAYER, root=Path(__file__).resolve().parents[2])
    report = result["report"]
    assert report["provider_status"] == "deferred_external"
    assert report["unresolved"]
    assert report["deterministic"]["memory-evals"]["passed"] is True


def test_provider_results_require_observation() -> None:
    layer = load_layer(LAYER)
    with pytest.raises(ValueError):
        LiveEvalReport(
            layer=layer,
            provider_status="deferred_external",
            provider_results={"x": 1},
            unresolved=("reason",),
        )


def test_frontier_unresolved_cost_carries_no_value() -> None:
    with pytest.raises(ValueError):
        FrontierPoint(profile="p", quality=1.0, cost=1.5, cost_state="unresolved")


def test_frontier_pareto_marks_dominant() -> None:
    frontier = build_frontier(
        {"accuracy": {"economy": 1.0, "deep": 1.0}},
        latencies_ms={"economy": 100.0, "deep": 900.0},
        costs=None,
    )
    pareto = {p.profile for p in frontier.points if p.pareto}
    assert pareto == {"economy"}
    assert any("cost unresolved" in u for u in frontier.unresolved)


def test_frontier_empty_accuracy_refuses() -> None:
    with pytest.raises(ContractError, match="AF-EVALS-FRONTIER"):
        build_frontier({"accuracy": {}})
