from apiforge.application.context import resolve_context
from apiforge.application.portable import initialize


def test_workspace_context_uses_independent_repositories(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    initialize(repo)
    result = resolve_context(repo, scope="repo")
    assert result.scope.scope == "repo"
    assert result.included_repositories
