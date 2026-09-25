from apiforge.application.experience_projection import project_result
from apiforge.application.portable import initialize


def test_portable_result_uses_canonical_experience_projection(tmp_path) -> None:
    result = initialize(tmp_path)

    projection = project_result("portable-init", result)

    assert projection.view.task_id == "portable-init"
    assert projection.view.status == "READY"
    assert projection.view.payload["mutation"] == "local-minimal-manifest-only"
