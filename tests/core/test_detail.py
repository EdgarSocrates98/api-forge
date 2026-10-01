import json

import pytest

from apiforge.core.detail import apply_detail_level

FINDINGS = [
    {
        "finding_id": "finding:a",
        "rule_id": "AF-CONTRACT-001",
        "title": "Contract operation has no implementation",
        "severity": "high",
        "status": "confirmed",
        "detail": "long human-readable detail body that costs tokens",
        "rationale": "why this matters, at length",
        "remediation": "how to fix, at length",
        "evidence": ["fact:1", "fact:2"],
    },
    {
        "finding_id": "finding:b",
        "rule_id": "AF-CODE-002",
        "title": "Code route missing from contract",
        "severity": "medium",
        "status": "confirmed",
        "detail": "more detail",
        "evidence": ["fact:3"],
    },
]

REPORT = {
    "ok": False,
    "refused": [
        {"code": "AF-SDD-GATE-BLOCKED", "field": "verify", "unlock": "produce evidence"},
    ],
    "unresolved": [],
    "findings": FINDINGS,
}


def test_summary_is_strictly_smaller() -> None:
    normal = json.dumps(apply_detail_level(REPORT, "normal"), sort_keys=True)
    summary = json.dumps(apply_detail_level(REPORT, "summary"), sort_keys=True)
    assert len(summary) < len(normal)


def test_summary_keeps_codes_and_fact_ids() -> None:
    summary = apply_detail_level(REPORT, "summary")
    assert summary["refused"][0]["code"] == "AF-SDD-GATE-BLOCKED"
    assert summary["findings"][0]["evidence"] == ["fact:1", "fact:2"]


def test_summary_is_a_pure_projection() -> None:
    original = apply_detail_level(REPORT, "summary")

    def subset(small, big):
        if isinstance(small, dict):
            return all(k in big and subset(v, big[k]) for k, v in small.items())
        if isinstance(small, list):
            return len(small) <= len(big) and all(
                subset(s, b) for s, b in zip(small, big, strict=False)
            )
        return small == big

    assert subset(original, REPORT)


def test_normal_is_passthrough() -> None:
    assert apply_detail_level(REPORT, "normal") == REPORT
    assert apply_detail_level(REPORT, "full") == REPORT


def test_unknown_level_is_refused() -> None:
    with pytest.raises(ValueError, match="AF-DETAIL-LEVEL"):
        apply_detail_level(REPORT, "verbose")
