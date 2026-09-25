"""Evidence-gated scorecard feedback for runtime evaluations."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from apiforge.capabilities.scorecard import build_scorecard, save_scorecard
from apiforge.contracts.agentic import AgentCapabilityProfile, AgentScorecard
from apiforge.contracts.base import ContractError
from apiforge.contracts.routing import ObservedSignal, ScorecardFeedback
from apiforge.evals.suite import EvalResult


def _gate_status(gate: Mapping[str, object]) -> str:
    return str(gate.get("status", "BLOCKED"))


def update_scorecard(
    root: Path,
    profile: AgentCapabilityProfile,
    results: tuple[EvalResult, ...],
    *,
    observations: tuple[ObservedSignal, ...] = (),
    gate: Mapping[str, object],
) -> tuple[ScorecardFeedback, AgentScorecard | None]:
    """Persist only feedback backed by a passing runtime evaluation gate."""
    status = _gate_status(gate)
    eval_refs = tuple(result.case_id for result in results)
    evidence = tuple(sorted({item for result in results for item in result.evidence}))
    gaps = tuple(
        sorted(
            {
                *(item for result in results for item in result.missing_evidence),
                *(item for result in results for item in result.failed_axes),
            }
        )
    )
    if status != "PASS":
        scorecard = build_scorecard(
            profile,
            results,
            observations=observations,
            allow_quality_promotion=False,
        )
        feedback = ScorecardFeedback(
            profile_id=profile.profile_id,
            status="blocked" if status == "BLOCKED" else "not_updated",
            gate_status=status,
            eval_refs=eval_refs,
            evidence=evidence,
            gaps=tuple(sorted({*gaps, "AF-RUNTIME-EVAL-GATE"})),
        )
        return feedback, scorecard
    if not results:
        raise ContractError(
            "AF-RUNTIME-EVAL-GATE",
            "field=results; unlock=provide persisted eval results before updating the scorecard",
        )
    if any(not result.evidence for result in results):
        raise ContractError(
            "AF-RUNTIME-EVAL-GATE",
            "field=results.evidence; unlock=preserve evidence refs for every eval result",
        )
    scorecard = build_scorecard(
        profile,
        results,
        observations=observations,
        allow_quality_promotion=True,
    )
    path = save_scorecard(root, scorecard)
    feedback = ScorecardFeedback(
        profile_id=profile.profile_id,
        status="updated",
        gate_status=status,
        scorecard_path=str(path),
        eval_refs=eval_refs,
        evidence=evidence,
        gaps=gaps,
    )
    return feedback, scorecard
