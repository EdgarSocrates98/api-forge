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
