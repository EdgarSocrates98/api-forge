"""Versioned contracts for deterministic capability routing."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import Field, model_validator

from apiforge.contracts.base import VersionedContract

RoutingSignalName = Literal["cost", "duration", "quality", "security"]
SignalStatus = Literal["observed", "unknown", "unresolved"]
RoutingObjective = Literal["efficiency", "quality"]


class ObservedSignal(VersionedContract):
    """A routing signal with explicit provenance and unknown-state semantics."""

    name: RoutingSignalName
    value: float | None = Field(default=None, ge=0)
    status: SignalStatus = "unknown"
    unit: str = ""
    source: str = "unknown"
    evidence_refs: tuple[str, ...] = ()

    @model_validator(mode="after")
    def observed_values_are_present(self) -> ObservedSignal:
        if self.status == "observed" and self.value is None:
            raise ValueError("observed routing signals require a value")
        if self.status != "observed" and self.value is not None:
            raise ValueError("unknown or unresolved routing signals cannot carry a value")
        return self


class RoutingPolicy(VersionedContract):
    """Configuration for the bounded first routing policy."""

    policy_id: str
    policy_version: str
    objective_order: tuple[RoutingObjective, ...] = ("efficiency", "quality")
    security_mode: Literal["gate"] = "gate"
    unknown_signal: Literal["unresolved"] = "unresolved"
    tie_breaker: Literal["capability"] = "capability"
    scorecard_update: Literal["eval_required"] = "eval_required"

    @model_validator(mode="after")
    def objectives_are_unique(self) -> RoutingPolicy:
        if len(set(self.objective_order)) != len(self.objective_order):
            raise ValueError("routing objective_order must not contain duplicates")
        return self


class RoutingRequest(VersionedContract):
    """Normalized task inputs consumed by eligibility and ranking."""

    task_id: str
    revision: int = Field(ge=0)
    risk: str
    requested_capabilities: tuple[str, ...] = ()
    required_evidence: tuple[str, ...] = ()
    available_evidence: tuple[str, ...] = ()
    inputs: tuple[str, ...] = ()
    policy_id: str


class CandidateAssessment(VersionedContract):
    """Explainable eligibility and ranking state for one candidate."""

    capability: str
    agent: str
    eligible: bool
    rejection: Mapping[str, str] | None = None
    signals: tuple[ObservedSignal, ...] = ()
    ranking_key: tuple[str, ...] = ()


class RoutingDecision(VersionedContract):
    """Persisted routing trace and deterministic execution order."""

    decision_id: str
    task_id: str
    revision: int = Field(ge=0)
    policy_id: str
    candidates: tuple[CandidateAssessment, ...] = ()
    selected: str | None = None
    fallback_order: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()


class ScorecardFeedback(VersionedContract):
    """Decision artifact for an evidence-gated scorecard update."""

    profile_id: str
    status: Literal["updated", "not_updated", "blocked"]
    gate_status: str
    scorecard_path: str | None = None
    eval_refs: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
