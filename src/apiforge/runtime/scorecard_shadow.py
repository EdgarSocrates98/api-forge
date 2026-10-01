"""Pure offline shadow comparison for scorecard-adaptive routing."""

from __future__ import annotations

from collections.abc import Sequence

from apiforge.contracts.scorecard_routing import ScorecardRoutingAssessment
from apiforge.contracts.scorecard_shadow import ScorecardShadowEvaluation, ShadowComparison
from apiforge.core.ids import stable_id


def evaluate_scorecard_shadow(
    *,
    assessment: ScorecardRoutingAssessment,
    baseline_policy_version: str,
    baseline_order: Sequence[str],
    adaptive_order: Sequence[str],
    baseline_selected: str | None,
    adaptive_selected: str | None,
) -> ScorecardShadowEvaluation:
    """Compare static and adaptive proposals without executing either route."""
    baseline = tuple(baseline_order)
    adaptive = tuple(adaptive_order)
    baseline_positions = {name: index for index, name in enumerate(baseline)}
    adaptive_positions = {name: index for index, name in enumerate(adaptive)}
    changed_candidates = tuple(
        sorted(
            name
            for name in baseline_positions
            if baseline_positions[name] != adaptive_positions.get(name)
        )
    )
    if adaptive_selected in assessment.selected_challengers:
        comparison: ShadowComparison = "challenger-selected"
    elif baseline == adaptive:
        comparison = "unchanged"
    else:
        comparison = "reordered"
    payload = {
        "assessment_id": assessment.assessment_id,
        "baseline_policy_version": baseline_policy_version,
        "adaptive_policy_version": assessment.policy_version,
        "baseline_order": baseline,
        "adaptive_order": adaptive,
        "baseline_selected": baseline_selected,
        "adaptive_selected": adaptive_selected,
        "selected_changed": baseline_selected != adaptive_selected,
        "changed_candidates": changed_candidates,
        "comparison": comparison,
        "evidence": assessment.evidence,
        "unresolved": assessment.unresolved,
    }
    return ScorecardShadowEvaluation(
        evaluation_id=stable_id("scorecard-shadow", payload),
        assessment_id=assessment.assessment_id,
        baseline_policy_version=baseline_policy_version,
        adaptive_policy_version=assessment.policy_version,
        baseline_order=baseline,
        adaptive_order=adaptive,
        baseline_selected=baseline_selected,
        adaptive_selected=adaptive_selected,
        selected_changed=baseline_selected != adaptive_selected,
        changed_candidates=changed_candidates,
        comparison=comparison,
        evidence=assessment.evidence,
        unresolved=assessment.unresolved,
    )
