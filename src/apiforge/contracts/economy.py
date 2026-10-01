"""Versioned economy contracts: per-emission cost vectors and run ledger entries."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract

LedgerSource = Literal["graph", "contract", "code", "knowledge", "filesystem", "envelope"]


class CostVector(VersionedContract):
    """Measured cost of one emission; tokens are observed or left unresolved."""

    context_bytes: int = Field(default=0, ge=0)
    tool_result_bytes: int = Field(default=0, ge=0)
    expansions: int = Field(default=0, ge=0)
    cache_hits: int = Field(default=0, ge=0)
    duration_ms: int = Field(default=0, ge=0)
    observed_tokens: int | None = Field(default=None, ge=0)


class LedgerRef(VersionedContract):
    """One ref attributed by a ledger entry, with the rule that selected it."""

    uri: str = Field(min_length=1)
    label: str = Field(min_length=1)
    provenance: str = Field(min_length=1)
    size_bytes: int = Field(ge=0)


class ProofReceipt(VersionedContract):
    """A proof a deterministic step produced: identity, kind and the hashed artifact."""

    proof_id: str = Field(min_length=1)
    kind: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    artifact_ref: str = Field(min_length=1)


class RunLedgerEntry(VersionedContract):
    """Attribution row appended to economy.jsonl alongside legacy transport rows."""

    schema: Literal["apiforge/run-ledger-entry/v1"] = "apiforge/run-ledger-entry/v1"  # type: ignore[assignment]
    run_id: str = Field(min_length=1)
    verb: str = Field(min_length=1)
    detail_level: str = "normal"
    source: LedgerSource
    cost: CostVector = Field(default_factory=CostVector)
    refs: tuple[LedgerRef, ...] = ()


EconomyProfile = Literal["economy", "balanced", "deep"]
ProfileSource = Literal["flag", "manifest", "policy"]
LadderLevel = Literal["L0", "L1", "L2", "L3", "L4", "L5"]
RiskClass = Literal["micro", "low", "medium", "high"]


class BudgetEnvelope(VersionedContract):
    """Hard execution limits for one profile; exhaustion is unresolved, never a downgrade."""

    profile: EconomyProfile
    provider_calls: int = Field(ge=1)
    fanout: int = Field(ge=0)
    fallbacks: int = Field(ge=0)
    debate_rounds: int = Field(ge=0)
    challenger_slots: int = Field(ge=0)
    verification_share: float = Field(ge=0.0, le=0.5)
    ladder_ceiling: LadderLevel
    context_bytes: int = Field(default=32000, ge=256)
    shadow_share: float = Field(default=0.0, ge=0.0, le=0.5)
    on_exhaustion: Literal["unresolved"] = "unresolved"
    silent_downgrade: Literal[False] = False


class LadderStep(VersionedContract):
    """One escalation step reached during a run and the trigger that caused it."""

    level: LadderLevel
    action: str = Field(min_length=1)
    trigger: str = Field(min_length=1)
    calls: int = Field(default=0, ge=0)


class EconomyPlan(VersionedContract):
    """Profile resolution, risk floor and envelope attached to a routing decision."""

    schema: Literal["apiforge/economy-plan/v1"] = "apiforge/economy-plan/v1"  # type: ignore[assignment]
    requested: EconomyProfile
    requested_source: ProfileSource
    floor: EconomyProfile
    effective: EconomyProfile
    escalation_reason: str | None = None
    envelope: BudgetEnvelope
    minimum_roles: tuple[str, ...] = ()
    trimmed_roles: tuple[str, ...] = ()
    escalation_reviewer: str | None = None
    stop_when: tuple[str, ...] = ("deterministic_proof", "no_unresolved_critical")
    diagnostics: tuple[str, ...] = ()


class RiskClassification(VersionedContract):
    """Deterministic change-risk class and the minimum SDD profile it requires."""

    schema: Literal["apiforge/risk-classification/v1"] = "apiforge/risk-classification/v1"  # type: ignore[assignment]
    risk_class: RiskClass
    sdd_profile: str = Field(min_length=1)
    signals: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
