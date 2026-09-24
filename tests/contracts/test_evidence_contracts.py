import pytest

from apiforge.contracts.evidence import EvidenceRecord, can_promote


def test_evidence_is_closed_and_normalized() -> None:
    record = EvidenceRecord(level="declared", source="fixture", refs=("b", "a", "a"))
    assert record.refs == ("a", "b")
    assert record.level == "declared"


def test_evidence_promotion_is_monotonic() -> None:
    assert can_promote("verified", "observed")
    assert not can_promote("heuristic", "verified")


def test_evidence_rejects_out_of_range_confidence() -> None:
    with pytest.raises(ValueError):
        EvidenceRecord(confidence=2.0)
