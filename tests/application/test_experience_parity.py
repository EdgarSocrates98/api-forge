from apiforge.application.experience_projection import project_result, project_status
from apiforge.application.portable import initialize
from apiforge.runtime.runner import run_runtime
from tests.runtime.test_runtime import make_task


def test_portable_result_uses_canonical_experience_projection(tmp_path) -> None:
    result = initialize(tmp_path)

    projection = project_result("portable-init", result)

    assert projection.view.task_id == "portable-init"
    assert projection.view.status == "READY"
    assert projection.view.payload["mutation"] == "local-minimal-manifest-only"


def test_runtime_projection_exposes_one_routing_assessment(tmp_path) -> None:
    make_task(tmp_path)
    run_runtime(tmp_path, "evolve-orders-api", now="2026-09-25T10:00:00+00:00")

    projection = project_status(tmp_path, "evolve-orders-api")

    assert projection.view.payload["routing"]["risk_complexity"]["complexity"] == "moderate"
    assert projection.view.payload["routing_plan"]["verification_depth"] == "elevated"
