from pathlib import Path

from apiforge.contracts.workspace import RepositoryRef, WorkspaceManifest
from apiforge.workspace.graph import build_graph


def test_workspace_graph_preserves_declared_evidence(tmp_path: Path) -> None:
    repository = RepositoryRef(repository_id="repository:a", name="a", root=str(tmp_path / "missing"))
    manifest = WorkspaceManifest(workspace_id="workspace:test", name="test", root=str(tmp_path), repositories=(repository,))
    graph = build_graph(manifest)
    membership = next(edge for edge in graph.edges if edge.relation == "contains")
    assert membership.evidence.level == "declared"
    assert graph.unresolved
    assert graph.evidence_level == "unknown"
