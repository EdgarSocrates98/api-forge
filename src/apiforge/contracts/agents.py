"""Agent roster contracts: host-neutral source, lint findings, routing eval."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract

AgentAccess = Literal["read-only", "state-writer", "writer"]
ModelTier = Literal["fast", "deep"]

REQUIRED_SECTIONS: tuple[str, ...] = (
    "When you enter",
    "When not to enter",
    "Inputs",
    "Method",
    "Output",
    "Done when",
    "Refusal and escalation",
    "Permissions",
    "Executors",
)


class AgentSource(VersionedContract):
    """One coordinator parsed from ``agents/<name>.md``."""

    name: str = Field(min_length=1)
    stem: str = Field(min_length=1)
    description: str = ""
    access: AgentAccess | None = None
    write_scope: str | None = None
    model_tier: ModelTier | None = None
    rule_areas: tuple[str, ...] = ()
    executors: tuple[str, ...] = ()
    apiforge_tools: tuple[str, ...] = ()
    replaces: tuple[str, ...] = ()
    body: str = ""
    raw: str = ""

    @property
    def legacy(self) -> bool:
        return self.access is None


class AgentFinding(VersionedContract):
    agent: str
    code: str
    field: str
    detail: str
    unlock: str


class AgentLintReport(VersionedContract):
    schema: Literal["apiforge/agent-lint/v1"] = "apiforge/agent-lint/v1"  # type: ignore[assignment]
    agents: int = Field(ge=0)
    passing: int = Field(ge=0)
    findings: tuple[AgentFinding, ...] = ()
    ok: bool


class AgentRoutingCase(VersionedContract):
    id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    expected: str = Field(min_length=1)
    family: str = Field(min_length=1)
    source: str = Field(min_length=1)


class AgentRoutingMiss(VersionedContract):
    id: str
    expected: str
    predicted: str
    top3: tuple[str, ...]


class AgentRoutingReport(VersionedContract):
    schema: Literal["apiforge/agent-routing-eval/v1"] = "apiforge/agent-routing-eval/v1"  # type: ignore[assignment]
    cases: int = Field(ge=0)
    agents: int = Field(ge=0)
    top1: float = Field(ge=0.0, le=1.0)
    top3: float = Field(ge=0.0, le=1.0)
    by_family: tuple[tuple[str, float], ...] = ()
    protected_misroutes: tuple[str, ...] = ()
    misses: tuple[AgentRoutingMiss, ...] = ()
    leakage_4gram: float = Field(default=0.0, ge=0.0, le=1.0)
    alias_mapping_applied: bool
    limitations: tuple[str, ...] = ()


__all__ = [
    "REQUIRED_SECTIONS",
    "AgentAccess",
    "AgentFinding",
    "AgentLintReport",
    "AgentRoutingCase",
    "AgentRoutingMiss",
    "AgentRoutingReport",
    "AgentSource",
    "ModelTier",
]
