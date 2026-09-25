"""Contracts for bounded repository, workspace and target context."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.evidence import EvidenceLevel, EvidenceRecord

ScopeKind = Literal["repo", "workspace", "target"]


class ContextScope(VersionedContract):
    """Closed selection vocabulary for context resolution."""

    scope: ScopeKind = "repo"
    root: str
    target: str | None = None
    impact: str | None = None


class ContextTarget(VersionedContract):
    """A target selected from observed repository/workspace inputs."""

    target_id: str
    label: str
    kind: str
    root: str
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)


class ContextResult(VersionedContract):
    """Canonical context result shared by CLI, MCP and host projections."""

    schema: Literal["apiforge/context/v1"] = "apiforge/context/v1"  # type: ignore[assignment]
    scope: ContextScope
    targets: tuple[ContextTarget, ...] = ()
    included_repositories: tuple[str, ...] = ()
    facts: tuple[dict[str, object], ...] = ()
    graph: dict[str, object] = Field(default_factory=dict)
    funnel: dict[str, object] = Field(default_factory=dict)
    evidence: tuple[EvidenceRecord, ...] = ()
    gaps: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
    status: Literal["ready", "degraded", "unresolved", "blocked"] = "ready"
    evidence_level: EvidenceLevel = "observed"
