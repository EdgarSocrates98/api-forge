"""Pure, bounded graph impact assessment over explicit local evidence."""

from __future__ import annotations

import json
from collections import deque
from collections.abc import Mapping, Sequence
from typing import Any

from apiforge.contracts.graph import GraphEdge, GraphExport, GraphNode
from apiforge.contracts.graph_impact import (
    GraphCandidateImpact,
    GraphFreshnessState,
    GraphGateState,
    GraphImpactAssessment,
    GraphImpactNode,
    GraphImpactPolicy,
    GraphSelectionEffect,
    default_graph_impact_policy,
)
from apiforge.contracts.risk_complexity import ReviewRole, VerificationDepth
from apiforge.core.ids import stable_id


def _prop_refs(props: Mapping[str, Any]) -> tuple[str, ...]:
    values: set[str] = set()
    for key in ("evidence_refs", "evidence", "source_refs"):
        raw = props.get(key)
        if isinstance(raw, str):
            values.add(raw)
        elif isinstance(raw, (list, tuple)):
            values.update(str(item) for item in raw)
    return tuple(sorted(values))


def _edge_ref(edge: GraphEdge) -> str:
    return f"{edge.from_id}->{edge.kind.value}->{edge.to_id}"


def _canonical_edges(edges: Sequence[GraphEdge]) -> tuple[GraphEdge, ...]:
    return tuple(
        sorted(
            edges,
            key=lambda item: (
                item.to_id,
                item.from_id,
                item.kind.value,
                json.dumps(dict(item.props), sort_keys=True, separators=(",", ":")),
            ),
        )
    )


def _walk(
    nodes: Mapping[str, GraphNode],
    edges: Sequence[GraphEdge],
    target_id: str,
    *,
    max_depth: int,
    max_nodes: int,
    max_edges: int,
    record_depth_limit: bool = True,
) -> tuple[dict[str, int], dict[str, set[str]], dict[str, set[str]], tuple[str, ...]]:
    adjacency: dict[str, list[GraphEdge]] = {}
    for edge in _canonical_edges(edges):
        adjacency.setdefault(edge.to_id, []).append(edge)
    queue: deque[tuple[str, int]] = deque([(target_id, 0)])
    depths: dict[str, int] = {}
    edge_refs: dict[str, set[str]] = {}
    evidence: dict[str, set[str]] = {}
    limitations: set[str] = set()
    traversed_edges = 0
    while queue:
        current, depth = queue.popleft()
        neighbors = adjacency.get(current, ())
        if depth >= max_depth:
            if neighbors and record_depth_limit:
                limitations.add(f"max_depth:{current}:{max_depth}")
            continue
        for edge in neighbors:
            if traversed_edges >= max_edges:
                limitations.add(f"max_edges:{max_edges}")
                return depths, edge_refs, evidence, tuple(sorted(limitations))
            traversed_edges += 1
            source_id = edge.from_id
            edge_refs.setdefault(source_id, set()).add(_edge_ref(edge))
            evidence.setdefault(source_id, set()).update(_prop_refs(edge.props))
            if source_id not in nodes:
                limitations.add(f"missing_node:{source_id}")
                continue
            if source_id == target_id:
                limitations.add(f"cycle:{source_id}")
                continue
            if source_id in depths:
                continue
            if len(depths) >= max_nodes:
                limitations.add(f"max_nodes:{max_nodes}")
                return depths, edge_refs, evidence, tuple(sorted(limitations))
            depths[source_id] = depth + 1
            evidence[source_id].update(_prop_refs(nodes[source_id].props))
            queue.append((source_id, depth + 1))
    return depths, edge_refs, evidence, tuple(sorted(limitations))


def _selection_for_candidate(
    candidate: str,
    refs: tuple[str, ...],
    *,
    known_ids: set[str],
    impacted_ids: set[str],
    effect: GraphSelectionEffect,
    unknown_effect: str,
) -> GraphCandidateImpact:
    evidence: set[str] = set()
    if not refs:
        selection: GraphSelectionEffect = "neutral" if unknown_effect == "static" else "unresolved"
        return GraphCandidateImpact(
            candidate=candidate,
            refs=refs,
            matched="unresolved",
            selection=selection,
            evidence=(f"candidate:{candidate}:graph-ref-missing",),
        )
    missing = tuple(ref for ref in refs if ref not in known_ids)
    if missing:
        evidence.update(f"candidate:{candidate}:missing-node:{ref}" for ref in missing)
        return GraphCandidateImpact(
            candidate=candidate,
            refs=refs,
            matched="unresolved",
            selection="unresolved",
            evidence=tuple(sorted(evidence)),
        )
    if impacted_ids.intersection(refs):
        evidence.add(f"candidate:{candidate}:explicit-impact")
        return GraphCandidateImpact(
            candidate=candidate,
            refs=refs,
            matched="explicit",
            selection=effect,
            evidence=tuple(sorted(evidence)),
        )
    evidence.add(f"candidate:{candidate}:explicit-ref-not-impacted")
    return GraphCandidateImpact(
        candidate=candidate,
        refs=refs,
        matched="none",
        selection="neutral",
        evidence=tuple(sorted(evidence)),
    )


def _effect_for_assessment(
    assessment_band: str,
    policy: GraphImpactPolicy,
    *,
    incomplete: bool,
) -> tuple[GraphGateState, VerificationDepth, tuple[ReviewRole, ...], GraphSelectionEffect]:
    effect = policy.effects[assessment_band]  # type: ignore[index]
    gate: GraphGateState = effect.gate_state
    depth: VerificationDepth = effect.verification_depth
    roles: tuple[ReviewRole, ...] = effect.required_roles
    selection = effect.selection
    if incomplete:
        if policy.incomplete_effect == "blocked":
            gate = "blocked"
            depth = "strict"
        elif depth == "standard":
            depth = "elevated"
    return gate, depth, roles, selection


def assess_graph_impact(
    nodes: Sequence[GraphNode],
    edges: Sequence[GraphEdge],
    target_id: str,
    *,
    mode: str | None = None,
    policy: GraphImpactPolicy | None = None,
    graph_snapshot: GraphExport | None = None,
    freshness_state: GraphFreshnessState = "fresh",
    candidate_refs: Mapping[str, Sequence[str]] | None = None,
    evidence: Sequence[str] = (),
) -> GraphImpactAssessment:
    """Assess explicit reverse impact with deterministic bounds and provenance."""
    selected_policy = policy or default_graph_impact_policy()
    selected_mode = mode or selected_policy.default_mode
    if selected_mode not in {"direct", "transitive", "all"}:
        raise ValueError(f"unsupported graph impact mode: {selected_mode!r}")
    canonical_nodes = {node.id: node for node in sorted(nodes, key=lambda item: item.id)}
    canonical_edges = _canonical_edges(edges)
    target = canonical_nodes.get(target_id)
    known_ids = set(canonical_nodes)
    unresolved: set[str] = set()
    limitations: set[str] = set()
    evidence_refs = {str(item) for item in evidence}
    if graph_snapshot is not None:
        evidence_refs.add(f"graph:nodes:{graph_snapshot.nodes_sha256}")
        evidence_refs.add(f"graph:edges:{graph_snapshot.edges_sha256}")
    evidence_refs.add(f"graph:target:{target_id}")

    if not canonical_nodes and graph_snapshot is None:
        coverage = "missing"
        unresolved.add(f"target:{target_id}:graph-missing")
        depths: dict[str, int] = {}
        edge_refs: dict[str, set[str]] = {}
        node_evidence: dict[str, set[str]] = {}
    elif target is None:
        coverage = "missing"
        unresolved.add(f"target:{target_id}:missing")
        depths = {}
        edge_refs = {}
        node_evidence = {}
    else:
        effective_depth = 1 if selected_mode == "direct" else selected_policy.max_depth
        depths, edge_refs, node_evidence, walk_limitations = _walk(
            canonical_nodes,
            canonical_edges,
            target_id,
            max_depth=effective_depth,
            max_nodes=selected_policy.max_nodes,
            max_edges=selected_policy.max_edges,
            record_depth_limit=selected_mode != "direct",
        )
        limitations.update(walk_limitations)
        if freshness_state != "fresh":
            unresolved.add(f"graph:freshness:{freshness_state}")
        if limitations or freshness_state != "fresh":
            coverage = "partial"
        else:
            coverage = "complete"

    if target is None or coverage in {"missing", "unresolved"}:
        impact_band = "unresolved"
    elif coverage == "partial":
        impact_band = "bounded"
    elif depths:
        impact_band = "explicit"
    else:
        impact_band = "none"
    incomplete = coverage != "complete" or freshness_state != "fresh"
    gate_state, verification_depth, required_roles, selection_effect = _effect_for_assessment(
        impact_band,
        selected_policy,
        incomplete=incomplete,
    )
    if incomplete and selected_policy.incomplete_effect == "blocked":
        unresolved.add("graph:incomplete:blocked-by-policy")
    impacted_nodes = tuple(
        GraphImpactNode(
            node_id=node_id,
            kind=canonical_nodes[node_id].kind,
            depth=depths[node_id],
            edge_refs=tuple(sorted(edge_refs.get(node_id, set()))),
            evidence=tuple(sorted(node_evidence.get(node_id, set()))),
        )
        for node_id in sorted(depths, key=lambda value: (depths[value], value))
    )
    impacted_ids = {target_id, *depths}
    candidate_impacts = tuple(
        _selection_for_candidate(
            candidate,
            tuple(sorted({str(ref) for ref in refs})),
            known_ids=known_ids,
            impacted_ids=impacted_ids,
            effect=selection_effect,
            unknown_effect=selected_policy.unknown_candidate_effect,
        )
        for candidate, refs in sorted((candidate_refs or {}).items())
    )
    for impacted_node in impacted_nodes:
        evidence_refs.update(impacted_node.edge_refs)
        evidence_refs.update(impacted_node.evidence)
    for candidate_impact in candidate_impacts:
        evidence_refs.update(candidate_impact.evidence)
        unresolved.update(
            candidate_impact.evidence if candidate_impact.matched == "unresolved" else ()
        )
    unresolved.update(limitations)
    if freshness_state == "unknown":
        unresolved.add("graph:freshness:unknown")
    identity_payload = {
        "target_id": target_id,
        "target_kind": target.kind.value if target is not None else None,
        "mode": selected_mode,
        "policy_version": selected_policy.policy_version,
        "policy": selected_policy.model_dump(mode="json"),
        "graph_snapshot": (
            graph_snapshot.model_dump(mode="json") if graph_snapshot is not None else None
        ),
        "freshness_state": freshness_state,
        "impacted_nodes": [item.model_dump(mode="json") for item in impacted_nodes],
        "candidate_refs": {
            key: tuple(sorted({str(ref) for ref in value}))
            for key, value in sorted((candidate_refs or {}).items())
        },
        "evidence": tuple(sorted(evidence_refs)),
        "unresolved": tuple(sorted(unresolved)),
        "limitations": tuple(sorted(limitations)),
    }
    assessment_id = stable_id("graph-impact", identity_payload)
    return GraphImpactAssessment(
        assessment_id=assessment_id,
        target_id=target_id,
        target_kind=target.kind if target is not None else None,
        mode=selected_mode,  # type: ignore[arg-type]
        policy_version=selected_policy.policy_version,
        graph_snapshot=graph_snapshot,
        coverage=coverage,  # type: ignore[arg-type]
        freshness_state=freshness_state,
        impact_band=impact_band,  # type: ignore[arg-type]
        impacted_nodes=impacted_nodes,
        candidate_impacts=candidate_impacts,
        gate_state=gate_state,
        verification_depth=verification_depth,
        required_roles=tuple(sorted(set(required_roles))),
        selection_effect=selection_effect,
        evidence=tuple(sorted(evidence_refs)),
        unresolved=tuple(sorted(unresolved)),
        limitations=tuple(sorted(limitations)),
    )


__all__ = ["assess_graph_impact"]
