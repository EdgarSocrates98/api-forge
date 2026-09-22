from __future__ import annotations

import pytest

from apiforge.perf.capacity import assess_capacity
from tests.perf.test_verdict import _complete_run


def test_capacity_assessment_emits_safe_envelope() -> None:
    assessment = assess_capacity(_complete_run())

    assert assessment.status == "passed"
    assert assessment.max_safe_tps == pytest.approx(81.6)
    assert "declared-headroom" in assessment.evidence


def test_capacity_assessment_never_hides_slo_failure() -> None:
    assessment = assess_capacity(_complete_run(p99_ms=900.0))

    assert assessment.status == "failed"
    assert assessment.max_safe_tps is None
    assert any(item.startswith("p99-within-slo:") for item in assessment.blockers)


def test_capacity_assessment_preserves_missing_evidence() -> None:
    assessment = assess_capacity(_complete_run(generator_dropped_iterations=None))

    assert assessment.status == "inconclusive"
    assert assessment.max_safe_tps is None
    assert any(item.startswith("generator-not-saturated:") for item in assessment.blockers)


def test_capacity_headroom_is_explicit_and_bounded() -> None:
    with pytest.raises(ValueError, match="headroom_pct"):
        assess_capacity(_complete_run(), headroom_pct=100.0)
