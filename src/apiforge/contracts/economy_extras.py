"""Economy wave 7 contracts: verification plans, retrieval, evidence nodes, doctor, tiers, prompts."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract

LadderLevel = Literal["V0", "V1", "V2", "V3", "V4", "V5"]


class SelectedTest(VersionedContract):
    path: str = Field(min_length=1)
    reasons: tuple[str, ...] = ()


class VerificationPlan(VersionedContract):
    """Targeted verification (§45–46): the cheapest ladder level the risk allows."""

    schema: Literal["apiforge/verification-plan/v1"] = "apiforge/verification-plan/v1"  # type: ignore[assignment]
    risk: Literal["micro", "low", "medium", "high"]
    level: LadderLevel
    changed: tuple[str, ...] = ()
    tests: tuple[SelectedTest, ...] = ()
    total_tests: int = Field(default=0, ge=0)
    commands: tuple[str, ...] = ()
    skipped_levels: tuple[LadderLevel, ...] = ()
    reasons: tuple[str, ...] = ()
    executes: Literal[False] = False


class Passage(VersionedContract):
    pack_id: str
    file: str
    heading: str
    score: float
    signals: dict[str, float] = Field(default_factory=dict)
    ref: str
    bytes: int = Field(ge=0)


class RetrievalResult(VersionedContract):
    """Deterministic expansion + ranking + progressive tiers (§56–58)."""

    schema: Literal["apiforge/retrieval-result/v1"] = "apiforge/retrieval-result/v1"  # type: ignore[assignment]
    query: str
    expanded_terms: tuple[str, ...] = ()
    added_terms: tuple[str, ...] = ()
    tier: int = Field(ge=1, le=3)
    passages: tuple[Passage, ...] = ()
    candidates: int = Field(default=0, ge=0)
    next_tier: int | None = None
    unresolved: tuple[str, ...] = ()


class EvidenceNode(VersionedContract):
    """One node of the evidence graph and its one-hop neighbors (§60)."""

    schema: Literal["apiforge/evidence-node/v1"] = "apiforge/evidence-node/v1"  # type: ignore[assignment]
    ref: str
    kind: str
    node_id: str
    props: dict[str, object] = Field(default_factory=dict)
    neighbors: tuple[str, ...] = ()
    source_ref: str | None = None
    unresolved: tuple[str, ...] = ()


class DoctorFinding(VersionedContract):
    code: str = Field(min_length=1)
    severity: Literal["info", "warning"]
    detail: str
    unlock: str


class EconomyDoctor(VersionedContract):
    """What in this setup makes runs pay more than they need to (§55)."""

    schema: Literal["apiforge/economy-doctor/v1"] = "apiforge/economy-doctor/v1"  # type: ignore[assignment]
    findings: tuple[DoctorFinding, ...] = ()
    checks: tuple[str, ...] = ()
    status: Literal["ok", "attention"] = "ok"


class ProviderCapability(VersionedContract):
    """Provider descriptor the Economy Plane reasons over — never provider names in core logic (§61)."""

    provider: str = Field(min_length=1)
    tier: Literal["T1", "T2", "T3"]
    structured_output: bool = False
    tool_calling: bool = False
    deferred_tools: bool = False
    context_window: int = Field(default=0, ge=0)
    reports_usage: bool = False
    cost_tier: Literal["local", "low", "medium", "high"] = "medium"
    local: bool = False


class TierDecision(VersionedContract):
    """Cheapest tier that evidence proves sufficient (§62)."""

    schema: Literal["apiforge/tier-decision/v1"] = "apiforge/tier-decision/v1"  # type: ignore[assignment]
    capability: str
    risk: str
    family: str | None = None
    tier: Literal["T0", "T1", "T2", "T3"]
    providers: tuple[str, ...] = ()
    reason: str


class PromptEnvelope(VersionedContract):
    """Stable prompt prefix + dynamic suffix (§81–83)."""

    schema: Literal["apiforge/prompt-envelope/v1"] = "apiforge/prompt-envelope/v1"  # type: ignore[assignment]
    capability: str
    prefix: str
    prefix_sha256: str
    suffix: str
    prefix_bytes: int = Field(ge=0)
    suffix_bytes: int = Field(ge=0)


class LocalityTier(VersionedContract):
    tier: Literal["target", "direct", "transitive"]
    repositories: tuple[str, ...] = ()
    included: bool = True
    reason: str = ""


class LocalityPlan(VersionedContract):
    """Workspace locality-first (§48–49): target, then direct, transitive only on request."""

    schema: Literal["apiforge/locality-plan/v1"] = "apiforge/locality-plan/v1"  # type: ignore[assignment]
    target: str
    tiers: tuple[LocalityTier, ...] = ()
    excluded: tuple[str, ...] = ()


__all__ = [
    "DoctorFinding",
    "EconomyDoctor",
    "EvidenceNode",
    "LocalityPlan",
    "LocalityTier",
    "Passage",
    "PromptEnvelope",
    "ProviderCapability",
    "RetrievalResult",
    "SelectedTest",
    "TierDecision",
    "VerificationPlan",
]
