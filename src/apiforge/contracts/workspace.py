"""Versioned contracts for project manifests and virtual workspaces."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.evidence import EvidenceLevel, EvidenceRecord

RepositoryType = Literal[
    "service",
    "library",
    "contract",
    "infrastructure",
    "frontend",
    "unknown",
]
RelationKind = Literal["contains", "depends_on", "client_of", "calls", "deploys"]


def _sorted_unique(value: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(set(value)))


class ProjectManifest(VersionedContract):
    """Minimal project connection state; knowledge and secrets stay packaged."""

    schema: Literal["apiforge/project/v1"] = "apiforge/project/v1"  # type: ignore[assignment]
    project_id: str
    root: str
    workspace_id: str | None = None
    default_scope: Literal["repo", "workspace", "target"] = "repo"
    target: str | None = None
    hosts: tuple[str, ...] = Field(default_factory=tuple)
    evidence_refs: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("hosts", "evidence_refs", mode="after")
    @classmethod
    def normalize_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _sorted_unique(value)


class RepositoryRef(VersionedContract):
    """A repository registered in a virtual workspace."""

    repository_id: str
    name: str
    root: str
    repository_type: RepositoryType = "unknown"
    project_manifest: str | None = None
    evidence_level: EvidenceLevel = "observed"
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)
    limitations: tuple[str, ...] = ()


class WorkspaceRelation(VersionedContract):
    """A bounded relationship claim with explicit provenance."""

    relation: RelationKind
    source: str
    from_id: str
    to_id: str
    evidence: EvidenceRecord = Field(default_factory=EvidenceRecord)
    limitations: tuple[str, ...] = ()


class WorkspaceManifest(VersionedContract):
    """Independent repository registry; it never turns repositories into a monorepo."""

    schema: Literal["apiforge/workspace/v1"] = "apiforge/workspace/v1"  # type: ignore[assignment]
    workspace_id: str
    name: str
    root: str
    repositories: tuple[RepositoryRef, ...] = ()
    relations: tuple[WorkspaceRelation, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    @field_validator("evidence_refs", mode="after")
    @classmethod
    def normalize_evidence_refs(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _sorted_unique(value)


class WorkspaceGraph(VersionedContract):
    """Deterministic graph payload with nodes, relations and unresolved gaps."""

    schema: Literal["apiforge/workspace-graph/v1"] = "apiforge/workspace-graph/v1"  # type: ignore[assignment]
    workspace_id: str
    nodes: tuple[dict[str, object], ...] = ()
    edges: tuple[WorkspaceRelation, ...] = ()
    unresolved: tuple[str, ...] = ()
    evidence_level: EvidenceLevel = "observed"


class WorkspaceStatus(VersionedContract):
    """Canonical workspace status returned by application services."""

    workspace: WorkspaceManifest | None = None
    graph: WorkspaceGraph | None = None
    discovered_project: ProjectManifest | None = None
    gaps: tuple[str, ...] = ()
    status: Literal["ready", "degraded", "unresolved", "blocked"] = "ready"
