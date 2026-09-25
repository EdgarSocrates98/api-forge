from pathlib import Path

from apiforge.application.runtime_experience import doctor, evolve, resume, review, status
from apiforge.runtime.adapters import FakeModelAdapter
from apiforge.runtime.runner import run_runtime
from tests.runtime.test_runtime import make_task


def test_runtime_experience_projects_canonical_commands(tmp_path: Path) -> None:
    make_task(tmp_path)
    evolved = evolve(tmp_path, "evolve-orders-api", now="2026-09-23T12:30:00+00:00")
    assert evolved["command"] == "evolve"
    assert evolved["status"] == "REVIEW"
    assert status(tmp_path, "evolve-orders-api")["command"] == "status"
    runtime_status = status(tmp_path, "evolve-orders-api")
    assert isinstance(runtime_status.get("routing"), dict)
    assert runtime_status["routing"]["risk_complexity"]["complexity"] == "moderate"
    assert doctor(tmp_path, "evolve-orders-api")["command"] == "doctor"
    assert review(tmp_path, "evolve-orders-api")["brief"]["status"] == "REVIEW"


def test_runtime_experience_resume_reuses_terminal_control_run(tmp_path: Path) -> None:
    make_task(tmp_path)
    evolve(tmp_path, "evolve-orders-api", now="2026-09-23T12:31:00+00:00")
    resumed = resume(tmp_path, "evolve-orders-api")
    assert resumed["command"] == "resume"
    assert resumed["resumed"] is True
    assert resumed["reused_invocations"] > 0


def test_runtime_experience_resume_executes_only_pending_step(tmp_path: Path) -> None:
    make_task(tmp_path)
    adapter = FakeModelAdapter({"api-security-review": {"__error__": "transient"}})
    first = run_runtime(
        tmp_path,
        "evolve-orders-api",
        adapter=adapter,
        now="2026-09-23T12:32:00+00:00",
    )
    assert first["status"] == "REVIEW"
    resumed = resume(tmp_path, "evolve-orders-api")
    assert resumed["resumed"] is True
    assert resumed["reused_invocations"] == 6
    assert len(resumed["artifacts"]) == 1
