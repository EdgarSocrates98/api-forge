"""Contracts for deterministic scorecard-adaptive routing."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.knowledge import FreshnessState

ScorecardLane = Literal["champion", "challenger", "unresolved"]
StaleScorecardBehavior = Literal["unresolved"]


class ScorecardRoutingPolicy(VersionedContract):
    """Local policy governing scorecard lanes and bounded exploration."""

    policy_version: str = "scorecard-routing/v1"
    min_evaluations: int = Field(default=1, ge=1)
    min_quality_score: float = Field(default=0.0, ge=0, le=1)
    challenger_slots: int = Field(default=1, ge=0, le=8)
    require_quality_promoted: bool = True
    stale_behavior: StaleScorecardBehavior = "unresolved"


class ScorecardCandidateAssessment(VersionedContract):
    """Explainable scorecard lane assignment for one routing candidate."""

    candidate: str
    profile_id: str | None = None
    lane: ScorecardLane
    eligible: bool
    quality_score: float | None = Field(default=None, ge=0, le=1)
    evaluation_count: int = Field(default=0, ge=0)
    freshness_state: FreshnessState = "unknown"
    quality_promoted: bool = False
    evidence: tuple[str, ...] = ()
    computed_from: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    reason_codes: tuple[str, ...] = ()

    @model_validator(mode="after")
    def champion_requires_fresh_promoted_history(self) -> ScorecardCandidateAssessment:
        if self.lane == "champion" and (
            not self.eligible or not self.quality_promoted or self.freshness_state != "fresh"
        ):
            raise ValueError("champion candidates require eligible fresh promoted history")
        return self


class ScorecardRoutingAssessment(VersionedContract):
    """Canonical scorecard-adaptive assessment embedded in a routing decision."""

    assessment_id: str
    policy_version: str
    candidates: tuple[ScorecardCandidateAssessment, ...] = ()
    champion_order: tuple[str, ...] = ()
    challenger_order: tuple[str, ...] = ()
    unresolved_order: tuple[str, ...] = ()
    ordered_candidates: tuple[str, ...] = ()
    selected_challengers: tuple[str, ...] = ()
    challenger_slots: int = Field(default=1, ge=0, le=8)
    evidence: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()

    @model_validator(mode="after")
    def selected_challengers_are_bounded(self) -> ScorecardRoutingAssessment:
        if len(self.selected_challengers) > self.challenger_slots:
            raise ValueError("selected challengers exceed challenger_slots")
        if not set(self.selected_challengers).issubset(self.challenger_order):
            raise ValueError("selected challengers must be present in challenger_order")
        if len(set(self.ordered_candidates)) != len(self.ordered_candidates):
            raise ValueError("ordered candidates must be unique")
        return self


def default_scorecard_routing_policy() -> ScorecardRoutingPolicy:
    """Return the safe local default used when a policy omits the extension."""
    return ScorecardRoutingPolicy()
