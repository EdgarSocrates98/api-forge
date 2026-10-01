from apiforge.contracts.workspace import WorkspaceManifest
from apiforge.workspace.graph import build_graph


def test_graph_ids_are_stable(tmp_path) -> None:
    manifest = WorkspaceManifest(workspace_id="workspace:test", name="test", root=str(tmp_path))
    assert build_graph(manifest).model_dump() == build_graph(manifest).model_dump()
