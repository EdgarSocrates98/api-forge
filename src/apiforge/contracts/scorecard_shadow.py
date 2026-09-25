"""Contracts for offline shadow comparison of adaptive routing."""

from __future__ import annotations

from typing import Literal

from pydantic import model_validator

from apiforge.contracts.base import VersionedContract

ShadowComparison = Literal["unchanged", "reordered", "challenger-selected"]


class ScorecardShadowEvaluation(VersionedContract):
    """A read-only comparison between static and adaptive route proposals."""

    evaluation_id: str
    assessment_id: str
    baseline_policy_version: str
    adaptive_policy_version: str
    baseline_order: tuple[str, ...] = ()
    adaptive_order: tuple[str, ...] = ()
    baseline_selected: str | None = None
    adaptive_selected: str | None = None
    selected_changed: bool = False
    changed_candidates: tuple[str, ...] = ()
    comparison: ShadowComparison = "unchanged"
    executed: Literal[False] = False
    evidence: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ("offline-only", "no-capability-invocation")

    @model_validator(mode="after")
    def comparison_is_consistent(self) -> ScorecardShadowEvaluation:
        if set(self.baseline_order) != set(self.adaptive_order):
            raise ValueError("shadow routes must compare the same candidate set")
        if len(set(self.baseline_order)) != len(self.baseline_order):
            raise ValueError("baseline shadow order must be unique")
        if len(set(self.adaptive_order)) != len(self.adaptive_order):
            raise ValueError("adaptive shadow order must be unique")
        if self.baseline_selected != (self.baseline_order[0] if self.baseline_order else None):
            raise ValueError("baseline selected must match the baseline order")
        if self.adaptive_selected != (self.adaptive_order[0] if self.adaptive_order else None):
            raise ValueError("adaptive selected must match the adaptive order")
        if self.selected_changed != (self.baseline_selected != self.adaptive_selected):
            raise ValueError("selected_changed must match the compared selections")
        return self
