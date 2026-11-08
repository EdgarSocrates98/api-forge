from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from apiforge.contracts.base import ContractError
from apiforge.runtime.control import ControlPlane


def _plane(tmp_path: Path) -> ControlPlane:
    return ControlPlane(tmp_path)


def test_control_plane_dynamic_ready_steps_and_review(tmp_path: Path) -> None:
    plane = _plane(tmp_path)
    run = plane.create(
        "api",
        (("inventory", ()), ("contract", ()), ("verify", ("inventory", "contract"))),
        max_parallel=2,
    )
    plan = plane.plan(run.run_id)
    assert plan["parallel_width"] == 2
    for step in plane.ready(run.run_id):
        plane.start(run.run_id, step.step_id)
        plane.complete(run.run_id, step.step_id, {"ok": True})
    assert plane.plan(run.run_id)["ready_steps"]
    verify = plane.ready(run.run_id)[0]
    plane.start(run.run_id, verify.step_id)
    plane.complete(run.run_id, verify.step_id, {"verified": True})
    assert plane.review(run.run_id, "independent-verifier", "approved").status == "completed"


def test_control_plane_retry_budget_and_cancel(tmp_path: Path) -> None:
    plane = _plane(tmp_path)
    run = plane.create("api", (("build", ()),), max_calls=2, max_retries=1)
    started = plane.start(run.run_id, run.steps[0].step_id)
    failed = plane.fail(run.run_id, started.steps[0].step_id, "transient")
    assert failed.steps[0].status == "pending"
    cancelled = plane.cancel(run.run_id, "human")
    assert cancelled.status == "cancelled"
    with pytest.raises(ContractError, match="AF-CONTROL-TERMINAL"):
        plane.start(run.run_id, run.steps[0].step_id)


def test_control_plane_replay_is_persisted(tmp_path: Path) -> None:
    plane = _plane(tmp_path)
    run = plane.create("api", (("inventory", ()),))
    plane.start(run.run_id, run.steps[0].step_id)
    replay = plane.replay(run.run_id)
    assert [event["event"] for event in replay["events"]] == ["planned", "step_started"]


def test_control_plane_completion_is_idempotent_and_conflict_safe(tmp_path: Path) -> None:
    plane = _plane(tmp_path)
    run = plane.create("api", (("verify", ()),))
    step = run.steps[0]
    plane.start(run.run_id, step.step_id)
    completed = plane.complete(run.run_id, step.step_id, {"ok": True})
    assert completed.steps[0].checkpoint_sha256 == completed.steps[0].result_sha256
    assert plane.complete(run.run_id, step.step_id, {"ok": True}).steps[0].status == "succeeded"
    with pytest.raises(ContractError, match="AF-CONTROL-IDEMPOTENCY-CONFLICT"):
        plane.complete(run.run_id, step.step_id, {"ok": False})


def test_control_plane_serializes_parallel_starts(tmp_path: Path) -> None:
    plane = _plane(tmp_path)
    run = plane.create(
        "api",
        tuple((f"step-{index}", ()) for index in range(8)),
        max_parallel=8,
        max_calls=8,
    )

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [
            pool.submit(plane.start, run.run_id, step.step_id)
            for step in run.steps
        ]
        started = [future.result() for future in futures]

    persisted = plane.get(run.run_id)
    assert len(started) == 8
    assert persisted.calls_used == 8
    assert {step.status for step in persisted.steps} == {"running"}
