from __future__ import annotations

from apiforge.runtime.control import ControlPlane


def test_control_plane_recovers_expired_worker_lease(tmp_path) -> None:
    plane = ControlPlane(tmp_path)
    run = plane.create("task:lease", (("extract", ()),), run_id="run:lease")
    step = run.steps[0]
    claimed = plane.claim(
        run.run_id, step.step_id, worker_id="worker-a", lease_until="2026-01-01T00:00:00+00:00"
    )
    assert claimed.steps[0].lease_owner == "worker-a"

    recovered = plane.recover_expired(run.run_id, now="2026-01-01T00:00:01+00:00")
    assert recovered.steps[0].status == "pending"
    assert recovered.steps[0].lease_owner is None
    assert plane.ready(run.run_id)[0].step_id == step.step_id
