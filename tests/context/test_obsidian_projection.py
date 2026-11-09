from apiforge.context.obsidian import build_obsidian_contract_review


def test_api_projection_carries_contract_review_sections_and_redacts_secrets():
    note = build_obsidian_contract_review(
        title="Orders API v2",
        summary="Review generated from the canonical contract analysis.",
        workspace="platform",
        vault_id="team-vault",
        endpoints=[{"method": "POST", "path": "/orders"}],
        breaking_changes=[{"code": "removed-field", "field": "legacy_id"}],
        security_review=[{"authorization_token": "do-not-write"}],
        related_refs=["adr://api/42"],
        e2e_notes=["token=do-not-write-text"],
    )
    assert note["schema"] == "theforge/ObsidianNoteRef/v1"
    assert "removed-field" in note["content"]
    assert "do-not-write" not in note["content"]
    assert "[REDACTED]" in note["content"]
