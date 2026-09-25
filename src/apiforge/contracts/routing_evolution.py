"""Contracts for evidence-gated routing evolution."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator, model_validator

from apiforge.contracts.base import VersionedContract

EvolutionMode = Literal["local", "replay", "shadow", "external-read"]
PromotionState = Literal["planned", "observed", "simulated", "active", "blocked"]
CoverageState = Literal["complete", "partial", "missing", "unresolved"]
PromotionStrategy = Literal["evidence_gated"]


class EvidenceCoverage(VersionedContract):
    """Explainable coverage of required evidence for one decision."""

    required: tuple[str, ...] = ()
    available: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()
    state: CoverageState = "unresolved"
    limitations: tuple[str, ...] = ()

    @field_validator("required", "available", "missing", "limitations", mode="after")
    @classmethod
    def normalize_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted(set(value)))

    @model_validator(mode="after")
    def coverage_is_consistent(self) -> EvidenceCoverage:
        expected_missing = set(self.required).difference(self.available)
        if set(self.missing) != expected_missing:
            raise ValueError("missing evidence must equal required minus available")
        if self.state == "complete" and self.missing:
            raise ValueError("complete evidence coverage cannot have missing evidence")
        if self.state == "missing" and self.available:
            raise ValueError("missing evidence coverage cannot have available evidence")
        return self


class EvolutionPolicy(VersionedContract):
    """Bounded policy for one routing evolution wave."""

    active_wave: int = Field(default=0, ge=0)
    mode: EvolutionMode = "local"
    promotion: PromotionStrategy = "evidence_gated"
    fallback: str = "static-routing"
    allow_external_mutation: bool = False
    require_rollback_ref: bool = True
    unknown_evidence: Literal["unresolved"] = "unresolved"
    adaptive_plan_enabled: bool = False
    adaptive_plan_max_steps: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def adaptive_plan_requires_bound(self) -> EvolutionPolicy:
        if self.adaptive_plan_enabled and self.adaptive_plan_max_steps is None:
            raise ValueError("adaptive plan requires a max_steps bound")
        if self.allow_external_mutation:
            raise ValueError("core evolution policy cannot allow external mutation")
        return self


class PromotionGate(VersionedContract):
    """Persisted evidence gate and promotion state for one routing decision."""

    decision_id: str
    mode: EvolutionMode
    state: PromotionState
    coverage: EvidenceCoverage
    evidence_refs: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    fallback: str = "static-routing"
    policy_version: str
    rollback_ref: str | None = None
    limitations: tuple[str, ...] = ()

    @field_validator("evidence_refs", "gaps", "limitations", mode="after")
    @classmethod
    def normalize_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(sorted(set(value)))

    @model_validator(mode="after")
    def active_requires_proof(self) -> PromotionGate:
        if self.state == "active":
            if self.mode != "local":
                raise ValueError("only local mode can become active in Wave 0")
            if self.coverage.state != "complete":
                raise ValueError("active promotion requires complete evidence coverage")
            if not self.evidence_refs or not self.rollback_ref:
                raise ValueError("active promotion requires evidence refs and rollback ref")
            if self.gaps:
                raise ValueError("active promotion cannot carry gaps")
        return self


class RoutingEvolution(VersionedContract):
    """Complete persisted evolution snapshot for a routing decision."""

    decision_id: str
    wave: int = Field(default=0, ge=0)
    policy_version: str
    gate: PromotionGate
    plan_digest: str | None = None
