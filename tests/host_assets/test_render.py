from apiforge.agentops.activation import render_host_preview


def test_host_preview_has_no_mutation(tmp_path):
    preview = render_host_preview("claude", str(tmp_path))
    assert preview["mutation"] == "none"
    assert preview["requires_approval"] is True
    assert preview["source_hash"]


def test_rel_seguro_descarta_traversal():
    """Refs `knowledge/<rel>` citadas em docs viram chaves de asset —
    `..`, absoluto, drive ou backslash nunca podem escapar do root."""
    from apiforge.install.render import _rel_seguro

    assert _rel_seguro("glue/workers.md")
    assert _rel_seguro("a/b/c.yaml")
    for bad in ("../../x.md", "../x.md", "/abs/x.md", "C:/x.md", "a\\b.md", "%2e%2e/x"):
        assert not _rel_seguro(bad), bad
