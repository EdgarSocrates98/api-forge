"""Economy-eval contracts: multi-axis matrix, evaluation gate, replay, role ROI, information gain.

Axes are kept separate on purpose (§72): a cheap wrong answer must never
look good because of a blended score.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract

Verdict = Literal["compatible", "breaking", "unresolved"]


class QualityAxis(VersionedContract):
    verdict: Verdict
    expected: Verdict
    verdict_ok: bool
    safety_ok: bool
    missing_roles: tuple[str, ...] = ()


class CostAxis(VersionedContract):
    calls: int = Field(ge=0)
    invocations: int = Field(ge=0)
    fanout: int = Field(ge=0)
    trimmed_roles: tuple[str, ...] = ()


class MatrixRow(VersionedContract):
    case_id: str = Field(min_length=1)
    profile: str = Field(min_length=1)
    holdout: bool = False
    status: str = ""
    quality: QualityAxis
    evidence: tuple[str, ...] = ()
    cost: CostAxis
    context_bytes: int = Field(default=0, ge=0)
    evidence_bytes: int = Field(default=0, ge=0)
    latency_ms: int = Field(default=0, ge=0)


class EconomyMatrix(VersionedContract):
    """Canonical task × profile matrix with per-axis aggregates and gates."""

    schema: Literal["apiforge/economy-matrix/v1"] = "apiforge/economy-matrix/v1"  # type: ignore[assignment]
    tasks: int = Field(ge=0)
    profiles: tuple[str, ...] = ()
    rows: tuple[MatrixRow, ...] = ()
    axes: dict[str, dict[str, float]] = Field(default_factory=dict)
    mutation: dict[str, int] = Field(default_factory=dict)
    gates: dict[str, bool] = Field(default_factory=dict)
    passed: bool = False
    tokens: Literal["unresolved"] = "unresolved"
    claim_scope: Literal["deterministic-safety-economy"] = "deterministic-safety-economy"


class EvaluationGate(VersionedContract):
    """Ship an economy change only without quality or safety regression (§76)."""

    schema: Literal["apiforge/evaluation-gate/v1"] = "apiforge/evaluation-gate/v1"  # type: ignore[assignment]
    decision: Literal["ship", "reject"]
    quality_regressions: tuple[str, ...] = ()
    safety_regressions: tuple[str, ...] = ()
    mutation_regression: bool = False
    holdout_regressions: tuple[str, ...] = ()
    max_quality_regression: int = Field(default=0, ge=0)
    calls_delta: dict[str, float] = Field(default_factory=dict)
    reasons: tuple[str, ...] = ()


class ReplayRun(VersionedContract):
    run: str = Field(min_length=1)
    profile: str
    status: Literal["same", "changed", "unresolved"]
    removed_required_roles: tuple[str, ...] = ()
    trimmed_before: tuple[str, ...] = ()
    trimmed_after: tuple[str, ...] = ()
    effective_before: str | None = None
    effective_after: str | None = None
    reason: str = ""


class ReplayReport(VersionedContract):
    """Stored decisions re-planned under the current policy, without providers (§77)."""

    schema: Literal["apiforge/replay-report/v1"] = "apiforge/replay-report/v1"  # type: ignore[assignment]
    runs: tuple[ReplayRun, ...] = ()
    changed: int = Field(default=0, ge=0)
    unresolved: int = Field(default=0, ge=0)
    removed_required_roles: int = Field(default=0, ge=0)
    passed: bool = True


class RoleROI(VersionedContract):
    """Did the extra agent change anything (§79)?"""

    capability: str = Field(min_length=1)
    runs: int = Field(ge=0)
    calls: int = Field(ge=0)
    facts_added: int = Field(ge=0)
    unresolved_added: int = Field(ge=0)
    outcome_changed: int = Field(ge=0)
    outcome_changed_rate: float = Field(ge=0.0, le=1.0)


class InformationGain(VersionedContract):
    """Expected gain of another agent after L2 (§80)."""

    level: Literal["low", "medium", "high"]
    reason: str = ""


__all__ = [
    "CostAxis",
    "EconomyMatrix",
    "EvaluationGate",
    "InformationGain",
    "MatrixRow",
    "QualityAxis",
    "ReplayReport",
    "ReplayRun",
    "RoleROI",
    "Verdict",
]
