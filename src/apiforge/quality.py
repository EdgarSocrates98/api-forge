"""Agentic quality aggregation for evals, holdouts and host parity."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from apiforge.contracts.stubs import AgenticQualityAssessment
from apiforge.evals.suite import EvalResult


def assess_agentic_quality(
    subject: str,
    results: Sequence[EvalResult],
    host_parity: Mapping[str, object],
) -> AgenticQualityAssessment:
    """Summarize quality without weakening individual eval verdicts."""

    passed = sum(result.verdict == "PASS" for result in results)
    blocked = sum(result.verdict == "BLOCKED" for result in results)
    review = len(results) - passed - blocked
    holdout = sum(bool(result.holdout_digest) for result in results)
    hosts = host_parity.get("hosts", {})
    gaps: list[str] = []
    if isinstance(hosts, Mapping):
        for name, value in sorted(hosts.items(), key=lambda item: str(item[0])):
            if isinstance(value, Mapping) and not value.get("ready_for_core", False):
                gaps.append(str(name))
    blockers: list[str] = []
    if blocked:
        blockers.append("blocked-eval-cases")
    if gaps:
        blockers.append("host-parity-gaps")
    if results and holdout < len(results):
        blockers.append("holdout-not-covered")
    status = "blocked" if blockers else ("review" if review else "ready")
    return AgenticQualityAssessment(
        id=f"quality-{subject}",
        subject=subject,
        status=status,  # type: ignore[arg-type]
        total_cases=len(results),
        passed_cases=passed,
        review_cases=review,
        blocked_cases=blocked,
        holdout_covered=holdout,
        host_gaps=tuple(gaps),
        blockers=tuple(blockers),
        evidence=("golden-evals", "holdout-evals", "host-parity"),
    )
