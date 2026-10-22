"""lf-0037: §6.2 discovery ops — manifest map, retrieval verbs, pointer stubs."""

from __future__ import annotations

from pathlib import Path


def test_ops_map_covers_all_fourteen():
    from apiforge import discovery_ops

    assert set(discovery_ops.ops()) == {
        "capabilities.list",
        "protocol.describe",
        "rules.search",
        "rules.get",
        "knowledge.search",
        "knowledge.get",
        "context.build",
        "health.check",
        # §7.2 (lf-0038): evals + verification
        "evals.list",
        "evals.describe",
        "evals.run",
        "evals.result",
        "verification.plan",
        "verification.run",
    }
    ids = {c["id"] for c in discovery_ops.commands()}
    assert set(discovery_ops.ops().values()) <= ids


def test_rules_search_pagination_and_filters():
    from apiforge import discovery

    p1 = discovery.rules_search(query="idempotency", limit=2)
    assert p1["total"] >= 2
    assert p1["next_cursor"] == "2"
    p2 = discovery.rules_search(query="idempotency", limit=2, cursor="2")
    assert {r["id"] for r in p1["rules"]} & {r["id"] for r in p2["rules"]} == set()
    sev = discovery.rules_search(severity="critical", index=True)
    assert all(r["severity"] == "critical" for r in sev["rules"])


def test_knowledge_search_get_provenance():
    import pytest

    from apiforge import discovery
    from apiforge.application.analyze import AnalysisError

    out = discovery.knowledge_search("idempotent", domain="api-design", limit=2)
    assert out["documents_total"] >= 1
    for d in out["documents"]:
        assert len(d["sha256"]) == 64
        assert d["matched_lines"] >= 1
    got = discovery.knowledge_get(out["documents"][0]["ref"])
    assert Path(got["document"]["path"]).is_file()
    assert len(got["document"]["sha256"]) == 64
    with pytest.raises(AnalysisError) as ei:
        discovery.knowledge_get("../pyproject.toml")
    assert ei.value.code == "AF-PATH-OUTSIDE-ROOT"
    with pytest.raises(AnalysisError) as ei2:
        discovery.rules_search(cursor="abc")
    assert ei2.value.code == "AF-CURSOR-INVALID"


def test_capabilities_and_context_pack_deterministic():
    from apiforge import discovery

    caps = discovery.capabilities()
    assert caps["rules"]["count"] > 0
    assert caps["knowledge"]["documents"] > 0
    assert len(caps["operations"]) == 14
    p1 = discovery.context_pack("data-access", rules_limit=5, knowledge_limit=3)
    p2 = discovery.context_pack("data-access", rules_limit=5, knowledge_limit=3)
    assert p1["pack_sha256"] == p2["pack_sha256"]
    assert len(p1["rules"]) <= 5 and len(p1["knowledge"]["documents"]) <= 3
    assert p1["operations"]["context.build"] == "context-pack"


def test_manifest_ops_consistent(tmp_path):
    from apiforge import _installkit as kit
    from apiforge import discovery_ops
    from apiforge.install.service import _context_manifest, _spec

    ctx = kit.InstallContext(
        spec=_spec(),
        scope="project",
        root=tmp_path,
        state_dir=tmp_path / ".apiforge",
        profile="recommended",
        hosts=("claude",),
    )
    m = _context_manifest(ctx)
    assert set(m["discovery"]["ops"]) == set(discovery_ops.ops())
    ids = {c["id"] for c in m["discovery"]["commands"]}
    assert set(m["discovery"]["ops"].values()) <= ids


def test_render_emits_knowledge_pointer_stub():
    from apiforge.install.render import render

    out = render(("devin",), skills=True, agents=True)
    stubs = {k: v for k, v in out.items() if k.startswith("knowledge/")}
    assert stubs, "expected pointer stubs for cited knowledge refs"
    for body in stubs.values():
        assert b"PONTEIRO" in body and b"apiforge knowledge" in body
