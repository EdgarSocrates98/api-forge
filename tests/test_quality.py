from apiforge.evals.suite import EvalResult
from apiforge.quality import assess_agentic_quality


def _result(verdict: str, digest: str | None = "a" * 64) -> EvalResult:
    return EvalResult("case", verdict, 1.0, holdout_digest=digest)


def test_quality_is_ready_with_passing_holdouts_and_hosts() -> None:
    result = assess_agentic_quality(
        "api-forge", [_result("PASS")], {"hosts": {"claude": {"ready_for_core": True}}}
    )
    assert result.status == "ready"
    assert result.holdout_covered == 1


def test_quality_blocks_uncovered_holdout_or_host_gap() -> None:
    result = assess_agentic_quality(
        "api-forge",
        [_result("PASS", None)],
        {"hosts": {"copilot": {"ready_for_core": False}}},
    )
    assert result.status == "blocked"
    assert set(result.blockers) == {"host-parity-gaps", "holdout-not-covered"}


def test_quality_preserves_review_cases() -> None:
    result = assess_agentic_quality(
        "api-forge", [_result("REVIEW")], {"hosts": {}}
    )
    assert result.status == "review"
    assert result.review_cases == 1
