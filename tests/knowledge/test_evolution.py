"""§29 knowledge engine evolution — drift, verified/deprecated states, impact graph."""

from pathlib import Path

import pytest

from apiforge.contracts.evidence import EvidenceRecord
from apiforge.contracts.knowledge import SourceObservation
from apiforge.knowledge.drift import detect_pack_drift
from apiforge.knowledge.freshness import verify_pack_freshness
from apiforge.knowledge.impact import build_knowledge_impact
from apiforge.knowledge.loader import load_pack, load_packs

NOW = "2026-10-01T00:00:00+00:00"


def _pack_dir(
    tmp_path: Path,
    *,
    freshness: str = "{window_days: 7, source_hash: abc123, source_version: v2}",
    rule_ids: str = "[AF-TEST-001]",
    evals: str = "",
) -> Path:
    directory = tmp_path / "demo-pack"
    directory.mkdir()
    (directory / "pack.yaml").write_text(
        "domain: demo-pack\nversion: 1\nareas: [REST]\n"
        f"rule_ids: {rule_ids}\n"
        f"freshness: {freshness}\n",
        encoding="utf-8",
    )
    (directory / "source_authority.yaml").write_text(
        "sources:\n  - name: demo-docs\n    url: https://example.com\n"
        "    authority: project-docs\n    verified: '2026-09-20'\n",
        encoding="utf-8",
    )
    if evals:
        (directory / "evals.yaml").write_text(evals, encoding="utf-8")
    return directory


def _receipt(
    observed_at: str, source_hash: str = "abc123", source_version: str | None = "v2"
) -> SourceObservation:
    return SourceObservation(
        source="demo-docs",
        observed_at=observed_at,
        source_hash=source_hash,
        source_version=source_version,
        receipt_ref="receipt:demo:1",
        evidence=EvidenceRecord(level="observed", source="read-only-adapter"),
    )


def test_freshness_verified_when_hash_and_version_match(tmp_path: Path) -> None:
    pack = load_pack(_pack_dir(tmp_path))
    result = verify_pack_freshness(pack, _receipt("2026-09-28T00:00:00+00:00"), now=NOW)
    assert result.state == "verified"


def test_freshness_fresh_when_version_not_compared(tmp_path: Path) -> None:
    pack = load_pack(_pack_dir(tmp_path))
    result = verify_pack_freshness(
        pack, _receipt("2026-09-28T00:00:00+00:00", source_version=None), now=NOW
    )
    assert result.state == "fresh"


def test_freshness_version_mismatch_is_stale(tmp_path: Path) -> None:
    pack = load_pack(_pack_dir(tmp_path))
    result = verify_pack_freshness(
        pack, _receipt("2026-09-28T00:00:00+00:00", source_version="v9"), now=NOW
    )
    assert result.state == "stale"


def test_freshness_expired_pack_is_deprecated(tmp_path: Path) -> None:
    pack = load_pack(
        _pack_dir(
            tmp_path,
            freshness=(
                "{window_days: 30, source_hash: abc123, expires_at: '2026-09-01T00:00:00Z'}"
            ),
        )
    )
    result = verify_pack_freshness(pack, _receipt("2026-09-28T00:00:00+00:00"), now=NOW)
    assert result.state == "deprecated"


def test_drift_unresolved_without_receipts(tmp_path: Path) -> None:
    pack = load_pack(_pack_dir(tmp_path))
    drift = detect_pack_drift(pack, (), now=NOW)
    assert drift.state == "unresolved"
    assert drift.unresolved


def test_drift_single_receipt_delegates(tmp_path: Path) -> None:
    pack = load_pack(_pack_dir(tmp_path))
    drift = detect_pack_drift(pack, (_receipt("2026-09-28T00:00:00+00:00"),), now=NOW)
    assert drift.state == "verified"
    assert drift.observations == 1


def test_drift_conflicting_receipts_is_conflicted(tmp_path: Path) -> None:
    pack = load_pack(_pack_dir(tmp_path))
    drift = detect_pack_drift(
        pack,
        (
            _receipt("2026-09-28T00:00:00+00:00", source_hash="abc123"),
            _receipt("2026-09-29T00:00:00+00:00", source_hash="fff999"),
        ),
        now=NOW,
    )
    assert drift.state == "conflicted"
    assert drift.conflicts
    assert "source_hash differs" in drift.conflicts[0]


def test_impact_graph_declared_relations(tmp_path: Path) -> None:
    packs_root = tmp_path / "packs"
    packs_root.mkdir()
    pack_dir = packs_root / "demo-pack"
    pack_dir.mkdir()
    (pack_dir / "pack.yaml").write_text(
        "domain: demo-pack\nversion: 1\nareas: [REST]\nrule_ids: [AF-TEST-001]\n",
        encoding="utf-8",
    )
    (pack_dir / "source_authority.yaml").write_text(
        "sources:\n  - name: demo-docs\n    url: https://example.com\n"
        "    authority: project-docs\n    verified: '2026-09-20'\n",
        encoding="utf-8",
    )
    (pack_dir / "evals.yaml").write_text(
        "evals:\n  - id: demo-pack/AF-TEST-001\n    type: golden\n"
        "    prompt: 'Which rule fires?'\n"
        "    expect: {kind: rule, id: AF-TEST-001}\n",
        encoding="utf-8",
    )
    skills_root = tmp_path / "skills"
    (skills_root / "demo-skill").mkdir(parents=True)
    (skills_root / "demo-skill" / "SKILL.md").write_text(
        "uses AF-TEST-001 for verification\n", encoding="utf-8"
    )
    report = build_knowledge_impact(
        packs_root, skills_root=skills_root, catalog={"AF-TEST-001": None}
    )
    edges = {(e.from_id, e.kind.value, e.to_id) for e in report.edges}
    assert ("pack:demo-pack", "backed_by", "source:project-docs:demo-docs") in edges
    assert ("pack:demo-pack", "contains", "rule:AF-TEST-001") in edges
    assert ("eval:demo-pack/AF-TEST-001", "verified_by", "rule:AF-TEST-001") in edges
    assert ("skill:demo-skill", "uses", "rule:AF-TEST-001") in edges
    assert report.totals["skills"] == 1
    assert any("agent -> knowledge" in u for u in report.unresolved)


def test_impact_graph_names_missing_catalog_rules(tmp_path: Path) -> None:
    packs_root = tmp_path / "packs"
    packs_root.mkdir()
    pack_dir = packs_root / "demo-pack"
    pack_dir.mkdir()
    (pack_dir / "pack.yaml").write_text(
        "domain: demo-pack\nversion: 1\nareas: []\nrule_ids: [AF-NOPE-999]\n",
        encoding="utf-8",
    )
    (pack_dir / "source_authority.yaml").write_text(
        "sources:\n  - name: demo-docs\n    url: https://example.com\n"
        "    authority: project-docs\n    verified: '2026-09-20'\n",
        encoding="utf-8",
    )
    report = build_knowledge_impact(packs_root, catalog={})
    assert any("AF-NOPE-999" in u for u in report.unresolved)


@pytest.mark.parametrize("domain", ["fastapi", "resilience", "api-dx"])
def test_real_packs_produce_declared_relations(domain: str) -> None:
    packs = load_packs(Path("knowledge"))
    assert domain in packs
    assert packs[domain].domain == domain
