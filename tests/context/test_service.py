from apiforge.application.context import resolve_context
from apiforge.application.portable import initialize


def test_context_service_returns_measured_local_funnel(tmp_path) -> None:
    initialize(tmp_path)

    result = resolve_context(tmp_path, scope="repo")

    assert result.scope.scope == "repo"
    assert result.funnel["diagnostics"]
    assert result.status == "degraded"
    assert result.unresolved
