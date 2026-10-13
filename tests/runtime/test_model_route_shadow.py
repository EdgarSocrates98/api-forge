"""Final-convergence phase 4: model routing runs in shadow inside ``execute_run``.

Every governed run now evaluates the §33 candidate router through
``route_model_shadow``: the §29 ``ShadowRecord`` lands in the control-plane
ledger, a ``ModelRouteShadowReceipt`` is persisted in the run artifacts, and
the declared adapter decision keeps governing — shadow can never mutate the
execution path. Inputs come only from declared run data (``model_route_*``
spec inputs, spec risk, risk-complexity assessment, call budget); signals the
caller did not declare stay ``None`` and land in ``unresolved``.
"""

from __future__ import annotations

import json
from pathlib import Path

from apiforge.contracts.task import TaskRisk, TaskSize, TaskSpec, TaskState
from apiforge.runtime.runner import run_runtime
from apiforge.taskspec.store import create
from tests.runtime.test_runtime import make_task


def _make_task(root: Path, *, extra_inputs: tuple[str, ...] = ()) -> TaskSpec:
    project = root / "project"
    project.mkdir()
    (project / "openapi.yaml").write_text("openapi: 3.0.0\n", encoding="utf-8")
    spec = TaskSpec(
        id="evolve-orders-api",
        outcome="produce a reviewed API evolution plan",
        size=TaskSize.M,
        inputs=(f"project={project}",) + extra_inputs,
        expected_proofs=("specialist artifact",),
        acceptance_criteria=("all findings are evidence bound",),
        rollback="discard local run artifacts",
        risk=TaskRisk.READ_ONLY,
        state=TaskState.SEALED,
        revision=1,
    )
    return create(root, spec)


def _run_dir(result: dict[str, object]) -> Path:
    return Path(str(result["run_dir"]))


def _receipt(result: dict[str, object]) -> dict[str, object]:
    path = _run_dir(result) / "model-route-shadow.json"
    assert path.is_file(), "model-route-shadow.json must persist inside the run dir"
    return json.loads(path.read_text(encoding="utf-8"))


def _shadow_ledger(root: Path) -> list[dict[str, object]]:
    path = root / ".apiforge" / "control-plane" / "shadow.jsonl"
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def test_execute_run_records_model_route_shadow_receipt(tmp_path: Path) -> None:
    make_task(tmp_path)
    result = run_runtime(tmp_path, "evolve-orders-api", now="2026-09-22T12:00:00+00:00")

    receipt = _receipt(result)
    assert receipt["schema"] == "apiforge/model-route-shadow-receipt/v1"
    assert receipt["route"] == "model_routing"
    # The route is declared shadow: the candidate never governs.
    assert receipt["mode"] == "shadow"
    assert receipt["governing"] == "legacy"
    assert receipt["control"]["shadow"] is True
    assert receipt["legacy_decision"]["selected"] == "fake"
    candidate = receipt["candidate"]
    assert candidate is not None and candidate["routing_kind"] == "model"
    assert receipt["recorded_at"]

    summary = json.loads((_run_dir(result) / "summary.json").read_text(encoding="utf-8"))
    assert summary["model_route_shadow"]["governing"] == "legacy"
    assert result["model_route_shadow"]["governing"] == "legacy"

    events = [
        json.loads(line)
        for line in (_run_dir(result) / "events.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert any(event["event"] == "model_route_shadow" for event in events)

    ledger = _shadow_ledger(tmp_path)
    assert len(ledger) == 1
    assert ledger[0]["route"] == "model_routing"
    assert ledger[0]["legacy_decision"]["selected"] == "fake"
    # candidate vs legacy divergence is persisted, not hidden
    assert ledger[0]["difference"]


def test_missing_signals_stay_unresolved_not_guessed(tmp_path: Path) -> None:
    make_task(tmp_path)
    result = run_runtime(tmp_path, "evolve-orders-api", now="2026-09-22T12:00:00+00:00")

    receipt = _receipt(result)
    inputs = receipt["inputs"]
    # Nothing was declared: the derived fields stay None and are named.
    assert inputs["task_class"] is None
    assert inputs["reasoning_needs"] is None
    assert inputs["context_size"] is None
    unresolved = set(receipt["unresolved"])
    assert {"task_class", "reasoning_needs", "context_size"} <= unresolved
    # Declared-by-runtime facts are still populated.
    assert inputs["risk"] == "read_only"
    assert inputs["needs_structured_output"] is True
    assert inputs["budget_remaining"]["calls"] >= 0


def test_declared_model_route_inputs_are_consumed(tmp_path: Path) -> None:
    _make_task(
        tmp_path,
        extra_inputs=(
            "model_route_task_class=analysis",
            "model_route_reasoning_needs=deep",
            "model_route_allow_challenger=true",
            "model_route_context_size=4000",
        ),
    )
    result = run_runtime(tmp_path, "evolve-orders-api", now="2026-09-22T12:00:00+00:00")

    receipt = _receipt(result)
    inputs = receipt["inputs"]
    assert inputs["task_class"] == "analysis"
    assert inputs["reasoning_needs"] == "deep"
    assert inputs["context_size"] == 4000
    assert inputs["allow_challenger"] is True
    assert receipt["invalid_inputs"] == []
    candidate = receipt["candidate"]
    # deep reasoning is a hard constraint: only the challenger tier qualifies,
    # and it is selectable because the spec declared allow_challenger.
    assert candidate["selected"] == "frontier-reviewer/frontier-reviewer-v1"
    assert receipt["governing"] == "legacy"


def test_invalid_declared_input_is_rejected_not_guessed(tmp_path: Path) -> None:
    _make_task(tmp_path, extra_inputs=("model_route_task_class=bogus",))
    result = run_runtime(tmp_path, "evolve-orders-api", now="2026-09-22T12:00:00+00:00")

    receipt = _receipt(result)
    assert receipt["invalid_inputs"] == ["task_class"]
    assert receipt["inputs"]["task_class"] is None
    assert "task_class" in receipt["unresolved"]
    assert receipt["governing"] == "legacy"


def test_no_eligible_model_is_an_explicit_refusal(tmp_path: Path) -> None:
    _make_task(tmp_path, extra_inputs=("model_route_context_size=99999999",))
    result = run_runtime(tmp_path, "evolve-orders-api", now="2026-09-22T12:00:00+00:00")

    receipt = _receipt(result)
    assert receipt["code"] == "AF-ROUTE-NO-ELIGIBLE-MODEL"
    assert receipt["candidate"]["selected"] is None
    assert all(not row["eligible"] for row in receipt["candidate"]["ranked"])
    # The refusal is still shadow-scoped: legacy keeps governing and the run
    # completes on the declared adapter.
    assert receipt["governing"] == "legacy"
    assert result["status"] in {"REVIEW", "BLOCKED"}


def test_declared_evaluations_feed_scorecards(tmp_path: Path) -> None:
    rows = [
        {
            "provider": "general-strong",
            "model": "general-strong-v1",
            "task_class": "analysis",
            "quality": 0.95,
            "evidence_correctness": 0.9,
            "latency_ms": 2400,
            "cost": 0.02,
            "recorded_at": "2026-09-20T00:00:00+00:00",
        }
        for _ in range(3)
    ]
    evals = tmp_path / "model-evals.jsonl"
    evals.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    _make_task(
        tmp_path,
        extra_inputs=(
            "model_route_task_class=analysis",
            "model_route_evaluations=model-evals.jsonl",
        ),
    )
    result = run_runtime(tmp_path, "evolve-orders-api", now="2026-09-22T12:00:00+00:00")

    receipt = _receipt(result)
    assert receipt["invalid_inputs"] == []
    ranked = {row["model"]: row for row in receipt["candidate"]["ranked"]}
    # quality 0.95 >= floor with 3 evaluations: the scorecard feeds the score.
    strong = ranked["general-strong-v1"]
    assert strong["eligible"] is True
    assert "scorecard-missing" not in strong["reasons"]


def test_evaluations_outside_root_are_refused(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-evals.jsonl"
    outside.write_text("{}\n", encoding="utf-8")
    _make_task(
        tmp_path,
        extra_inputs=(f"model_route_evaluations={outside}",),
    )
    result = run_runtime(tmp_path, "evolve-orders-api", now="2026-09-22T12:00:00+00:00")

    receipt = _receipt(result)
    assert "model_route_evaluations" in receipt["invalid_inputs"]
    assert "AF-PATH-OUTSIDE-ROOT" in receipt["unresolved"]
    assert receipt["governing"] == "legacy"
