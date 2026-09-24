from pathlib import Path

from apiforge.contracts.evidence import EvidenceRecord
from apiforge.contracts.knowledge import SourceObservation
from apiforge.knowledge.freshness import verify_pack_freshness
from apiforge.knowledge.loader import load_pack


def _pack(tmp_path: Path, window: int = 7) -> Path:
    directory = tmp_path / "fresh-pack"
    directory.mkdir()
    (directory / "pack.yaml").write_text(
        f"domain: fresh-pack\nversion: 1\nareas: []\nrule_ids: []\n"
        f"freshness: {{window_days: {window}, source_hash: abc123}}\n",
        encoding="utf-8",
    )
    (directory / "source_authority.yaml").write_text(
        "sources:\n  - name: source\n    url: https://example.com\n"
        "    authority: project-docs\n    verified: '2026-09-20'\n",
        encoding="utf-8",
    )
    return directory


def _observation(observed_at: str, source_hash: str = "abc123") -> SourceObservation:
    return SourceObservation(
        source="source",
        observed_at=observed_at,
        source_hash=source_hash,
        receipt_ref="receipt:source:1",
        evidence=EvidenceRecord(level="observed", source="read-only-adapter"),
    )


def test_freshness_fresh_stale_and_unresolved(tmp_path: Path) -> None:
    pack = load_pack(_pack(tmp_path))
    now = "2026-09-23T00:00:00+00:00"
    assert (
        verify_pack_freshness(pack, _observation("2026-09-20T00:00:00+00:00"), now=now).state
        == "fresh"
    )
    assert (
        verify_pack_freshness(pack, _observation("2026-09-01T00:00:00+00:00"), now=now).state
        == "stale"
    )
    assert verify_pack_freshness(pack, None, now=now).state == "unresolved"


def test_freshness_hash_mismatch_is_stale(tmp_path: Path) -> None:
    pack = load_pack(_pack(tmp_path))
    result = verify_pack_freshness(
        pack,
        _observation("2026-09-22T00:00:00+00:00", source_hash="different"),
        now="2026-09-23T00:00:00+00:00",
    )
    assert result.state == "stale"
