from apiforge.workspace.service import WorkspaceService


def test_workspace_init_and_add_preserve_independent_repository(tmp_path) -> None:
    workspace = tmp_path / "workspace"
    repository = tmp_path / "service"
    repository.mkdir()
    service = WorkspaceService(workspace)
    service.init(workspace=True, name="platform")
    manifest = service.add(repository)
    assert len(manifest.repositories) == 1
    assert manifest.repositories[0].root == str(repository.resolve())
