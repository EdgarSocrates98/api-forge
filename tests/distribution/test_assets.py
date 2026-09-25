from apiforge.host_assets.loader import load_asset, load_manifest, render_template


def test_packaged_assets_are_read_only_and_hashable() -> None:
    _content, digest = load_asset("templates/AGENTS.md.tmpl")
    rendered, rendered_digest = render_template(
        "templates/AGENTS.md.tmpl", {"generator": "test", "source_hash": digest}
    )
    assert "test" in rendered
    assert digest
    assert rendered_digest
    assert load_manifest()["schema"] == "apiforge/host-assets/v1"
