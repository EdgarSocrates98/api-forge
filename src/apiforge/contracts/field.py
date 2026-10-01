"""Field-validation contracts: pre-registered corpus, per-task run records, gap report."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract

Scenario = Literal["maintenance", "evolution", "security", "multi_repo", "incident", "performance"]
ExitReason = Literal[
    "knowledge_gap",
    "capability_gap",
    "context_gap",
    "graph_gap",
    "tool_gap",
    "ux_gap",
    "evaluation_gap",
    "integration_gap",
    "none",
]
FieldPhase = Literal["baseline", "ab_on"]
RepoKind = Literal["own", "oss"]
VerifierVerdict = Literal["agree", "disagree", "unresolved"]
H1Verdict = Literal["confirmed", "refuted", "inconclusive"]
ActorKind = Literal["human", "agent"]
CycleStatus = Literal["collecting", "ready", "expired"]
VerificationState = Literal["agree", "disagree", "unresolved", "stale"]
_SHA = r"^[0-9a-f]{64}$"

SCENARIOS: tuple[str, ...] = (
    "maintenance",
    "evolution",
    "security",
    "multi_repo",
    "incident",
    "performance",
)
EXIT_REASONS: tuple[str, ...] = (
    "knowledge_gap",
    "capability_gap",
    "context_gap",
    "graph_gap",
    "tool_gap",
    "ux_gap",
    "evaluation_gap",
    "integration_gap",
    "none",
)
IDENTITY_COMPONENTS: tuple[str, ...] = (
    "cycle_started_at",
    "corpus_sha256",
    "hypothesis_sha256",
    "gate_sha256",
    "tasks_sha256",
    "repos_sha256",
)


class FieldGate(VersionedContract):
    max_runs: int = Field(default=40, ge=1)
    max_weeks: int = Field(default=4, ge=1)
    min_tasks_per_theme: int = Field(default=5, ge=1)
    min_repos_per_theme: int = Field(default=2, ge=1)
    min_tasks_per_scenario: int = Field(default=5, ge=1)


class FieldHypothesis(VersionedContract):
    id: str = Field(min_length=1)
    category: ExitReason
    refutation: str = Field(min_length=1)


class CorpusRepo(VersionedContract):
    ref: str = Field(min_length=1)
    kind: RepoKind


class GroundTruth(VersionedContract):
    kind: str = Field(min_length=1)
    ref: str = Field(min_length=1)


class CorpusTask(VersionedContract):
    id: str = Field(min_length=1)
    scenario: Scenario
    repo_ref: str = Field(min_length=1)
    registered_at: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    ground_truth: GroundTruth


class CorpusManifest(VersionedContract):
    schema: Literal["apiforge/field-corpus/v1"] = "apiforge/field-corpus/v1"  # type: ignore[assignment]
    cycle_started_at: str | None = None
    gate: FieldGate = Field(default_factory=FieldGate)
    hypothesis: FieldHypothesis
    repos: tuple[CorpusRepo, ...] = ()
    tasks: tuple[CorpusTask, ...] = ()


class ActorRef(VersionedContract):
    kind: ActorKind
    id: str = Field(min_length=1)


class VerificationReceipt(VersionedContract):
    schema: Literal["apiforge/field-verification-receipt/v1"] = (
        "apiforge/field-verification-receipt/v1"  # type: ignore[assignment]
    )
    verdict: VerifierVerdict
    annotation_sha256: str = Field(pattern=_SHA)
    verifier: ActorRef
    verified_at: str = Field(min_length=1)


class FieldCycleIdentity(VersionedContract):
    """What a sealed field cycle pre-registered; every field command must match it."""

    schema: Literal["apiforge/field-cycle-identity/v1"] = "apiforge/field-cycle-identity/v1"  # type: ignore[assignment]
    cycle_started_at: str = Field(min_length=1)
    corpus_sha256: str = Field(pattern=_SHA)
    hypothesis_sha256: str = Field(pattern=_SHA)
    gate_sha256: str = Field(pattern=_SHA)
    tasks_sha256: str = Field(pattern=_SHA)
    repos_sha256: str = Field(pattern=_SHA)
    git_commit: str | None = None

    def first_difference(self, other: FieldCycleIdentity) -> str | None:
        """First sealed component that differs; ``git_commit`` is informational."""
        for name in IDENTITY_COMPONENTS:
            if getattr(self, name) != getattr(other, name):
                return name
        return None

    def same_cycle(self, other: FieldCycleIdentity) -> bool:
        return self.first_difference(other) is None


class CoverageGate(VersionedContract):
    enough_scenarios: bool
    runs_total: int = Field(ge=0)
    max_runs: int = Field(ge=1)
    deadline: str | None = None
    within_timebox: bool


class FieldRun(VersionedContract):
    schema: Literal["apiforge/field-run/v2"] = "apiforge/field-run/v2"  # type: ignore[assignment]
    task_id: str = Field(min_length=1)
    scenario: Scenario
    repo_ref: str = Field(min_length=1)
    phase: FieldPhase
    executor: ActorRef
    run_ids: tuple[str, ...] = Field(min_length=1)
    inference_flag: bool
    started_at: str
    ended_at: str
    provider_calls: int | None = Field(default=None, ge=0)
    context_bytes: int | None = Field(default=None, ge=0)
    cache_reuse: int | None = Field(default=None, ge=0)
    time_to_evidence_ms: int | None = Field(default=None, ge=0)
    time_to_solution_ms: int | None = Field(default=None, ge=0)
    task_completed: bool | None = None
    exit_reason: ExitReason | None = None
    manual_context_required: bool | None = None
    human_intervention: bool | None = None
    false_positives: int | None = Field(default=None, ge=0)
    false_negatives: int | None = Field(default=None, ge=0)
    verification: VerificationReceipt | None = None
    sources: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()


class ThemeCount(VersionedContract):
    exit_reason: ExitReason
    count: int = Field(ge=0)
    repos: int = Field(ge=0)
    share: float = Field(ge=0.0, le=1.0)
    ci95: tuple[float, float]
    qualified: bool


class AbDelta(VersionedContract):
    task_id: str
    baseline_manual_context: bool | None
    ab_manual_context: bool | None
    baseline_time_to_solution_ms: int | None
    ab_time_to_solution_ms: int | None
    time_delta_ms: int | None


class FieldReport(VersionedContract):
    schema: Literal["apiforge/field-report/v2"] = "apiforge/field-report/v2"  # type: ignore[assignment]
    cycle_status: CycleStatus
    coverage_gate: CoverageGate
    runs_total: int = Field(ge=0)
    runs_verified: int = Field(ge=0)
    repos: int = Field(ge=0)
    scenario_counts: tuple[tuple[str, int], ...] = ()
    scenarios_under_min: tuple[str, ...] = ()
    themes: tuple[ThemeCount, ...] = ()
    qualified_themes: tuple[str, ...] = ()
    hypothesis: FieldHypothesis
    provisional_h1: H1Verdict
    h1_verdict: H1Verdict
    divergence_rate: float = Field(ge=0.0, le=1.0)
    contaminated_runs: tuple[str, ...] = ()
    unresolved_runs: tuple[str, ...] = ()
    stale_runs: tuple[str, ...] = ()
    ab: tuple[AbDelta, ...] = ()
    recommendation: str


__all__ = [
    "EXIT_REASONS",
    "IDENTITY_COMPONENTS",
    "SCENARIOS",
    "AbDelta",
    "ActorKind",
    "ActorRef",
    "CorpusManifest",
    "CorpusRepo",
    "CorpusTask",
    "CoverageGate",
    "CycleStatus",
    "ExitReason",
    "FieldCycleIdentity",
    "FieldGate",
    "FieldHypothesis",
    "FieldPhase",
    "FieldReport",
    "FieldRun",
    "GroundTruth",
    "H1Verdict",
    "Scenario",
    "ThemeCount",
    "VerificationReceipt",
    "VerificationState",
]
