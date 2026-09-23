"""Versioned contracts for API, Git and CI/CD change governance."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Literal

from pydantic import Field, StringConstraints, field_validator

from apiforge.contracts.base import VersionedContract
from apiforge.core.models import JsonValue, Sha256, freeze_json

CommitSha = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]
ChangeOrigin = Literal["pull_request", "branch", "manual", "replay"]
ChangeProvider = Literal["github", "artifact"]
CheckConclusion = Literal[
    "success",
    "failure",
    "neutral",
    "cancelled",
    "skipped",
    "timed_out",
    "action_required",
    "unknown",
]
GovernanceStatus = Literal["ok", "review", "blocked", "failed"]
SupportState = Literal["supported", "heuristic", "unresolved", "unsupported"]


class ChangeSource(VersionedContract):
    """A provenance pointer that can be independently re-hashed."""

    provider: ChangeProvider
    kind: Literal["pull_request", "compare", "check_run", "artifact", "manual"]
    reference: str
    sha256: Sha256
    observed_at: str


class ChangeCheck(VersionedContract):
    """Read-only CI/CD observation normalized from a provider payload."""

    name: str
    conclusion: CheckConclusion
    source: ChangeSource
    details: Mapping[str, JsonValue] = Field(default_factory=dict)

    @field_validator("details", mode="after")
    @classmethod
    def freeze_details(cls, value: object) -> Mapping[str, JsonValue]:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise TypeError("check details must be a JSON object")
        return frozen


class ChangeArtifact(VersionedContract):
    """An input or output artifact referenced by a change bundle."""

    name: str
    reference: str
    sha256: Sha256
    source: ChangeSource


class ChangePolicy(VersionedContract):
    """Policy facts carried with a bundle so decisions remain auditable."""

    read_only: bool = True
    mutation_allowed: bool = False
    untrusted_input: bool = True
    limitations: tuple[str, ...] = ()


class ChangeCollectRequest(VersionedContract):
    """Inputs for a GitHub read-only collection operation."""

    repository: str
    base_sha: CommitSha
    head_sha: CommitSha
    origin: ChangeOrigin = "pull_request"
    pull_number: int | None = Field(default=None, ge=1)
    contract: str | None = None
    baseline: str | None = None
    project: str | None = None
    api_base: str = "https://api.github.com"


class ChangeBundle(VersionedContract):
    """Provider-neutral input to the deterministic change-control pipeline."""

    schema_version: Literal["af-change-bundle/1"] = "af-change-bundle/1"
    repository: str
    base_sha: CommitSha
    head_sha: CommitSha
    origin: ChangeOrigin
    provider: ChangeProvider = "artifact"
    pull_number: int | None = Field(default=None, ge=1)
    contract: str | None = None
    baseline: str | None = None
    project: str | None = None
    diff: str | None = None
    sources: tuple[ChangeSource, ...] = ()
    checks: tuple[ChangeCheck, ...] = ()
    artifacts: tuple[ChangeArtifact, ...] = ()
    policy: ChangePolicy = Field(default_factory=ChangePolicy)
    limitations: tuple[str, ...] = ()


class Recommendation(VersionedContract):
    """Explainable recommendation shape used by agents and deterministic evals."""

    recommendation: str
    facts: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    alternatives: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    verifier: str
    confidence: float = Field(ge=0, le=1)


class RecommendationEvaluation(VersionedContract):
    """Outcome of comparing a recommendation against a declared oracle."""

    status: Literal["pass", "review", "fail"]
    dataset: str
    case_id: str
    matched_requirements: tuple[str, ...] = ()
    missing_requirements: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


class ChangeControlResult(VersionedContract):
    """Stable public result for CLI, MCP, IDE and UI projections."""

    capability_id: str = "api.change-control"
    state: SupportState
    status: GovernanceStatus
    payload: Mapping[str, JsonValue] = Field(default_factory=dict)
    evidence: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    error_code: str | None = None

    @field_validator("payload", mode="after")
    @classmethod
    def freeze_payload(cls, value: object) -> Mapping[str, JsonValue]:
        frozen = freeze_json(value)
        if not isinstance(frozen, Mapping):
            raise TypeError("change-control payload must be a JSON object")
        return frozen
