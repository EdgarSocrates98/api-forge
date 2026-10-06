"""Contracts for bounded repository, workspace and target context."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.evidence import EvidenceLevel, EvidenceRecord

ScopeKind = Literal["repo", "workspace", "target"]
RefKind = Literal["contract", "schema", "code", "test", "policy", "knowledge"]
RefOrigin = Literal["graph", "contract", "code", "knowledge", "filesystem"]
CapsuleLevel = Literal["L0", "L1", "L2", "L3", "L4"]
CTX_URI_PATTERN = r"^ctx://sha256/[0-9a-f]{64}$"


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


class ContextRef(VersionedContract):
    """Content-addressed pointer to one piece of evidence held in the ctx store."""

    uri: str = Field(pattern=CTX_URI_PATTERN)
    kind: RefKind
    label: str = Field(min_length=1)
    source: str = Field(min_length=1)
    span: tuple[int, int] | None = None
    revision: str = "worktree"
    size_bytes: int = Field(ge=0)
    provenance: str = Field(min_length=1)
    origin: RefOrigin
    level: CapsuleLevel = "L3"
    parity: bool | None = None
    delta: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    excerpt: str | None = None


class CapsuleBudget(VersionedContract):
    """Deterministic byte ceiling and the level the selection actually reached."""

    context_bytes: int = Field(ge=256)
    max_level: CapsuleLevel = "L3"
    serialized_bytes: int = Field(default=0, ge=0)
    reached_level: CapsuleLevel = "L0"


class CapsuleRefusal(VersionedContract):
    """A cataloged refusal carried inside a partial capsule."""

    code: str = Field(pattern=r"^AF-[A-Z0-9-]+$")
    field: str = Field(min_length=1)
    unlock: str = Field(min_length=1)
    detail: str = ""


class ContextCapsule(VersionedContract):
    """Minimal sufficient evidence for one intent, addressed by ctx:// refs."""

    schema: Literal["apiforge/context-capsule/v1"] = "apiforge/context-capsule/v1"  # type: ignore[assignment]
    capsule_id: str = Field(pattern=CTX_URI_PATTERN)
    run_id: str = Field(min_length=1)
    intent: dict[str, str]
    scope: ContextScope
    fingerprint: dict[str, object] = Field(default_factory=dict)
    impact: dict[str, int] = Field(default_factory=dict)
    refs: tuple[ContextRef, ...] = ()
    policies: tuple[str, ...] = ()
    expertise: tuple[str, ...] = ()
    budget: CapsuleBudget
    refusals: tuple[CapsuleRefusal, ...] = ()
    unresolved: tuple[str, ...] = ()
    status: Literal["ready", "degraded", "unresolved"] = "ready"

    @model_validator(mode="after")
    def refs_are_unique(self) -> ContextCapsule:
        uris = [ref.uri for ref in self.refs]
        if len(set(uris)) != len(uris):
            raise ValueError("capsule refs must be unique")
        return self
