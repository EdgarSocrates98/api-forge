from apiforge.agentops.activation import render_host_preview


def test_host_preview_has_no_mutation(tmp_path):
    preview = render_host_preview("claude", str(tmp_path))
    assert preview["mutation"] == "none"
    assert preview["requires_approval"] is True
    assert preview["source_hash"]
