"""Versioned contracts for deterministic graph-aware routing impact."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import Field, model_validator

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.graph import GraphExport, NodeKind
from apiforge.contracts.risk_complexity import ReviewRole, VerificationDepth

GraphImpactMode = Literal["direct", "transitive", "all"]
GraphImpactCoverage = Literal["complete", "partial", "missing", "unresolved"]
GraphFreshnessState = Literal["fresh", "stale", "unresolved", "unknown"]
GraphImpactBand = Literal["none", "explicit", "bounded", "unresolved"]
GraphGateState = Literal["open", "review", "blocked"]
GraphSelectionEffect = Literal["prefer", "neutral", "demote", "exclude", "unresolved"]
GraphCandidateMatch = Literal["explicit", "none", "unresolved"]


class GraphImpactEffect(VersionedContract):
    """Policy effect for a graph impact band."""

    gate_state: GraphGateState = "open"
    verification_depth: VerificationDepth = "standard"
    required_roles: tuple[ReviewRole, ...] = ()
    selection: GraphSelectionEffect = "neutral"

    @model_validator(mode="after")
    def values_are_unique(self) -> GraphImpactEffect:
        if len(set(self.required_roles)) != len(self.required_roles):
            raise ValueError("graph impact required_roles must be unique")
        return self


class GraphImpactPolicy(VersionedContract):
    """Bounded local policy for graph traversal and routing effects."""

    policy_version: str = Field(min_length=1)
    default_mode: GraphImpactMode = "transitive"
    max_depth: int = Field(default=4, ge=1, le=64)
    max_nodes: int = Field(default=256, ge=1, le=4096)
    max_edges: int = Field(default=1024, ge=1, le=16384)
    incomplete_effect: Literal["elevated", "blocked"] = "elevated"
    unknown_candidate_effect: Literal["static", "unresolved"] = "unresolved"
    effects: Mapping[GraphImpactBand, GraphImpactEffect]

    @model_validator(mode="after")
    def policy_is_complete(self) -> GraphImpactPolicy:
        expected = {"none", "explicit", "bounded", "unresolved"}
        missing = expected.difference(self.effects)
        if missing:
            raise ValueError(f"graph impact effects missing: {sorted(missing)}")
        return self


class GraphImpactNode(VersionedContract):
    """One explicitly reached graph node and its local evidence."""

    node_id: str = Field(min_length=1)
    kind: NodeKind
    depth: int = Field(ge=1)
    edge_refs: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()


class GraphCandidateImpact(VersionedContract):
    """Graph evidence used to explain one candidate's selection effect."""

    candidate: str = Field(min_length=1)
    refs: tuple[str, ...] = ()
    matched: GraphCandidateMatch = "unresolved"
    selection: GraphSelectionEffect = "unresolved"
    evidence: tuple[str, ...] = ()


class GraphImpactAssessment(VersionedContract):
    """Canonical, replayable graph impact result consumed by routing and briefs."""

    assessment_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    target_kind: NodeKind | None = None
    mode: GraphImpactMode
    policy_version: str = Field(min_length=1)
    graph_snapshot: GraphExport | None = None
    coverage: GraphImpactCoverage
    freshness_state: GraphFreshnessState
    impact_band: GraphImpactBand
    impacted_nodes: tuple[GraphImpactNode, ...] = ()
    candidate_impacts: tuple[GraphCandidateImpact, ...] = ()
    gate_state: GraphGateState = "open"
    verification_depth: VerificationDepth = "standard"
    required_roles: tuple[ReviewRole, ...] = ()
    selection_effect: GraphSelectionEffect = "neutral"
    evidence: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @model_validator(mode="after")
    def values_are_unique(self) -> GraphImpactAssessment:
        node_ids = [item.node_id for item in self.impacted_nodes]
        candidate_names = [item.candidate for item in self.candidate_impacts]
        if len(set(node_ids)) != len(node_ids):
            raise ValueError("graph impact node ids must be unique")
        if len(set(candidate_names)) != len(candidate_names):
            raise ValueError("graph impact candidate names must be unique")
        if len(set(self.required_roles)) != len(self.required_roles):
            raise ValueError("graph impact required_roles must be unique")
        return self


def default_graph_impact_policy() -> GraphImpactPolicy:
    """Return the conservative, bounded graph-impact policy."""
    return GraphImpactPolicy(
        policy_version="graph-impact/v1",
        default_mode="transitive",
        max_depth=4,
        max_nodes=256,
        max_edges=1024,
        incomplete_effect="elevated",
        unknown_candidate_effect="unresolved",
        effects={
            "none": GraphImpactEffect(),
            "explicit": GraphImpactEffect(
                gate_state="review",
                verification_depth="elevated",
                required_roles=("reviewer",),
                selection="prefer",
            ),
            "bounded": GraphImpactEffect(
                gate_state="review",
                verification_depth="strict",
                required_roles=("reviewer", "critic"),
                selection="prefer",
            ),
            "unresolved": GraphImpactEffect(
                gate_state="review",
                verification_depth="elevated",
                required_roles=("reviewer",),
                selection="unresolved",
            ),
        },
    )


__all__ = [
    "GraphCandidateImpact",
    "GraphCandidateMatch",
    "GraphFreshnessState",
    "GraphGateState",
    "GraphImpactAssessment",
    "GraphImpactBand",
    "GraphImpactCoverage",
    "GraphImpactEffect",
    "GraphImpactMode",
    "GraphImpactNode",
    "GraphImpactPolicy",
    "GraphSelectionEffect",
    "default_graph_impact_policy",
]
