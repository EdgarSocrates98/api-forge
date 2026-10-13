from apiforge.context.resolver import resolve_scope


def test_repo_scope_resolves_from_nested_path(tmp_path):
    root = tmp_path / "repo"
    nested = root / "src"
    (root / ".git").mkdir(parents=True)
    nested.mkdir()
    scope, _ = resolve_scope(nested, scope="repo")
    assert scope.root == str(root.resolve())
