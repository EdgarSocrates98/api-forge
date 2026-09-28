"""Economy wave 8 contracts: freshness watch, live gating, escalation, phase budgets, checkpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.economy import EconomyProfile

WatchState = Literal["fresh", "refresh_needed", "unknown", "unresolved"]
EvidenceMode = Literal["static", "fixture", "live_read_only"]
QuestionClass = Literal["static", "runtime", "ambiguous"]
VerdictState = Literal[
    "missing", "likely", "clear", "confirmed", "passed", "failed", "inconclusive"
]
EscalationAction = Literal["run_tests", "escalate", "stop", "unresolved"]
PhaseStatus = Literal["within", "exceeded", "protected_overrun", "unmeasured"]


class PackWatchEntry(VersionedContract):
    pack_id: str
    domain: str
    state: WatchState
    upstream: str | None = None
    declared_fingerprint: str | None = None
    upstream_fingerprint: str | None = None
    declared_version: str | None = None
    upstream_version: str | None = None
    reasons: tuple[str, ...] = ()
    next_action: str = "none"


class FreshnessWatch(VersionedContract):
    """§96: which packs need a refresh, compared against a local upstream manifest."""

    schema: Literal["apiforge/freshness-watch/v1"] = "apiforge/freshness-watch/v1"  # type: ignore[assignment]
    now: str
    manifest_sha256: str | None = None
    entries: tuple[PackWatchEntry, ...] = ()
    refresh_needed: tuple[str, ...] = ()
    fetches: Literal[False] = False


class LiveEvidenceDecision(VersionedContract):
    """§97: whether a question may pay for live read-only evidence."""

    schema: Literal["apiforge/live-evidence-decision/v1"] = "apiforge/live-evidence-decision/v1"  # type: ignore[assignment]
    question: str
    question_class: QuestionClass
    mode: EvidenceMode
    live_allowed: bool
    runtime_terms: tuple[str, ...] = ()
    static_terms: tuple[str, ...] = ()
    suggested_sources: tuple[str, ...] = ()
    requires_receipt: bool = False
    escalate_if_unanswered: bool = False
    reasons: tuple[str, ...] = ()


class VerificationEscalation(VersionedContract):
    """§99: next step after static analysis and tests; never past live_read_only."""

    schema: Literal["apiforge/verification-escalation/v1"] = "apiforge/verification-escalation/v1"  # type: ignore[assignment]
    static: VerdictState
    test: VerdictState
    runtime: VerdictState
    action: EscalationAction
    next_mode: Literal["test", "live_read_only"] | None = None
    reason: str
    test_evidence: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()


class PhaseBudget(VersionedContract):
    phase: str
    share: float = Field(ge=0.0, le=1.0)
    calls: int = Field(ge=0)
    context_bytes: int = Field(ge=0)
    protected: bool = False
    used_calls: int | None = Field(default=None, ge=0)
    used_context_bytes: int | None = Field(default=None, ge=0)
    status: PhaseStatus = "unmeasured"


class PhaseBudgetPlan(VersionedContract):
    """§104: the profile envelope split across SDD phases."""

    schema: Literal["apiforge/phase-budget-plan/v1"] = "apiforge/phase-budget-plan/v1"  # type: ignore[assignment]
    profile: EconomyProfile
    total_calls: int = Field(ge=0)
    total_context_bytes: int = Field(ge=0)
    phases: tuple[PhaseBudget, ...] = ()
    status: Literal["ok", "unresolved"] = "ok"
    codes: tuple[str, ...] = ()


class EconomyCheckpoint(VersionedContract):
    """§104: budget already spent by a run, persisted so a resume continues it."""

    schema: Literal["apiforge/economy-checkpoint/v1"] = "apiforge/economy-checkpoint/v1"  # type: ignore[assignment]
    run_id: str
    task_id: str
    requested: EconomyProfile
    effective: EconomyProfile
    max_calls: int = Field(ge=0)
    calls_used: int = Field(ge=0)
    calls_remaining: int = Field(ge=0)
    stopped_at: str | None = None
    resumes: int = Field(default=0, ge=0)
    updated_at: str
    status: Literal["ok", "unresolved"] = "ok"
    codes: tuple[str, ...] = ()


__all__ = [
    "EconomyCheckpoint",
    "FreshnessWatch",
    "LiveEvidenceDecision",
    "PackWatchEntry",
    "PhaseBudget",
    "PhaseBudgetPlan",
    "VerificationEscalation",
]
