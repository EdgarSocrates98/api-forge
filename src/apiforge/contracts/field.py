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


class FieldGate(VersionedContract):
    max_runs: int = Field(default=30, ge=1)
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


class FieldRun(VersionedContract):
    schema: Literal["apiforge/field-run/v1"] = "apiforge/field-run/v1"  # type: ignore[assignment]
    task_id: str = Field(min_length=1)
    scenario: Scenario
    repo_ref: str = Field(min_length=1)
    phase: FieldPhase
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
    verifier_verdict: VerifierVerdict | None = None
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
    schema: Literal["apiforge/field-report/v1"] = "apiforge/field-report/v1"  # type: ignore[assignment]
    runs_total: int = Field(ge=0)
    runs_verified: int = Field(ge=0)
    repos: int = Field(ge=0)
    scenario_counts: tuple[tuple[str, int], ...] = ()
    scenarios_under_min: tuple[str, ...] = ()
    themes: tuple[ThemeCount, ...] = ()
    qualified_themes: tuple[str, ...] = ()
    hypothesis: FieldHypothesis
    h1_verdict: H1Verdict
    divergence_rate: float = Field(ge=0.0, le=1.0)
    contaminated_runs: tuple[str, ...] = ()
    unresolved_runs: tuple[str, ...] = ()
    ab: tuple[AbDelta, ...] = ()
    recommendation: str


__all__ = [
    "EXIT_REASONS",
    "SCENARIOS",
    "AbDelta",
    "CorpusManifest",
    "CorpusRepo",
    "CorpusTask",
    "ExitReason",
    "FieldGate",
    "FieldHypothesis",
    "FieldPhase",
    "FieldReport",
    "FieldRun",
    "GroundTruth",
    "H1Verdict",
    "Scenario",
    "ThemeCount",
]
