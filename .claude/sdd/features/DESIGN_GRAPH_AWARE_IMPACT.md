# DESIGN: Graph-Aware Impact

> Technical design for implementing the deterministic, evidence-preserving graph impact assessment used by routing, selection and explainable projections.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | GRAPH_AWARE_IMPACT |
| **Date** | 2026-09-25 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_GRAPH_AWARE_IMPACT.md](./DEFINE_GRAPH_AWARE_IMPACT.md) |
| **Status** | ✅ Complete (Built) |

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────────┐
│                 GRAPH-AWARE IMPACT / OFFLINE MVP                     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  TaskSpec + optional graph target/mappings                           │
│              │                                                       │
│              ▼                                                       │
│  [local graph JSONL] ──read/verify──▶ [GraphImpactAssessor]          │
│        nodes.jsonl / edges.jsonl             │                        │
│        + GraphExport/v1                       │                        │
│                                                ▼                       │
│                                  [GraphImpactAssessment/v1]           │
│                                  explicit nodes/edges/paths           │
│                                  coverage/freshness/gaps              │
│                                     │             │                   │
│                      ┌──────────────┘             └──────────────┐    │
│                      ▼                                             ▼    │
│              [routing gate]                              [candidate rank]│
│              additive to A                           explicit refs only  │
│              and policy effect                       unresolved fallback  │
│                      │                                             │    │
│                      └─────────────────┬───────────────────────────┘    │
│                                        ▼                                │
│                             [RoutingDecision/v1]                        │
│                             [RoutingPlan/v1]                            │
│                             [routing.json / routing-plan.json]         │
│                                        │                                │
│                                        ▼                                │
│                         [runtime / governance / owner brief]           │
│                         same stored assessment, no re-traversal        │
│                                                                      │
│  No provider, network, database, model SDK or graph mutation path.   │
└──────────────────────────────────────────────────────────────────────┘
```

The MVP keeps graph file I/O at the existing graph-store boundary and keeps traversal, policy combination and candidate effects pure. The supervisor loads a verified local snapshot once, passes typed graph data to the assessor, and persists the resulting assessment inside the routing artifacts. Every downstream projection reads that assessment from the decision or stored run artifacts; it never performs an independent traversal.

The existing risk/complexity assessment remains authoritative for task risk, complexity, verification depth and required roles. Graph impact is an additive policy input: the effective gate is the most conservative of the two assessments, and an unresolved graph state can only preserve or increase verification requirements.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| Graph impact contracts | Define immutable `GraphImpactPolicy/v1`, `GraphImpactAssessment/v1`, impacted nodes and candidate evidence with closed vocabularies | Pydantic v2 `BaseModel`, existing `VersionedContract` |
| Graph impact assessor | Run bounded reverse traversal over explicit `GraphNode`/`GraphEdge` data, classify coverage and derive policy effects | Pure Python, deterministic sorting, existing graph contracts |
| Graph snapshot adapter | Load and validate `nodes.jsonl`, `edges.jsonl` and `GraphExport/v1` at the supervisor boundary | Existing `apiforge.graph.store.read_graph` |
| Routing adapter | Feed one assessment into the existing risk gate, candidate ranking, scorecard adaptation and decision identity | Existing `runtime/routing.py`, A/B routing contracts |
| Run artifact persistence | Store the assessment as part of the canonical routing decision and plan artifacts | Existing `RunStore`, JSON serialization |
| Experience projections | Expose the stored impact explanation to runtime, governance and capability-owner views | Existing `runtime_experience` and brief renderers |
| Offline fixture/evaluation suite | Prove replay, traversal modes, bounds, conservative fallback, selection, compatibility and no external calls | pytest, JSON/YAML fixtures, existing evaluation harness |

---

## Key Decisions

### Decision 1: Canonical immutable assessment rather than a graph score

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-25 |

**Context:** Routing, governance and capability owners need the same explanation of impact. A scalar score would lose the explicit nodes, edge evidence, traversal limits and unresolved diagnostics required by API Forge's evidence contract.

**Choice:** Introduce a frozen `GraphImpactAssessment/v1`. Its identity is a stable hash of the canonical graph snapshot reference, target, mode, bounds, policy version, candidate references and ordered input evidence. The assessment contains typed impacted nodes, explicit edge/path evidence, coverage, freshness, policy effect, candidate effects and unresolved limitations.

**Rationale:** A single immutable artifact can be used by the gate, selection and projections without recomputation. It is replayable, inspectable and compatible with the existing versioned Pydantic contracts and `stable_id` convention.

**Alternatives Rejected:**
1. Numeric graph-impact score - rejected because an opaque number cannot preserve provenance or distinguish missing evidence from low impact.
2. Recalculate impact independently in each consumer - rejected because it permits drift between the gate, selected candidate and brief.

**Consequences:**
- The assessment is larger than a score and must be serialized in routing artifacts.
- Any future schema change requires a new versioned contract or an explicit compatibility adapter.

---

### Decision 2: Explicit bounded reverse traversal with conservative unknown state

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-25 |

**Context:** The graph store already contains directed, explicit provenance edges and has a bounded reverse-impact query. Cycles, missing targets, stale exports and traversal budgets must not create an unsafe authorization or an unbounded runtime.

**Choice:** Implement `assess_graph_impact()` as a pure function over typed graph data. Reverse adjacency follows `GraphEdge.to_id -> GraphEdge.from_id`, only explicit edges are traversed, neighbors are sorted by `(node_id, edge_kind)`, and the walk is bounded by `max_depth`, `max_nodes` and `max_edges`. A visited map records the first deterministic depth; cycles are retained as limitations rather than traversed again. A missing target, invalid snapshot, stale state or budget cutoff is represented as `unresolved`/`partial`, then evaluated by policy.

**Rationale:** This reuses the canonical local graph boundary, preserves deterministic replay and guarantees termination without adding a graph database or inferred relationship layer.

**Alternatives Rejected:**
1. Unbounded breadth-first traversal - rejected because graph size and cycles would make latency and memory non-deterministic.
2. Heuristic or model-inferred edges - rejected because inference would violate the explicit-evidence and offline requirements.

**Consequences:**
- A bounded graph can legitimately produce `partial` coverage; the unresolved reason must stay visible.
- The assessor must operate on canonical input order and never depend on filesystem iteration order.

---

### Decision 3: Policy effects are additive and monotonic with A/B routing

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-25 |

**Context:** The feature must change verification and selection without replacing the existing risk/complexity and scorecard semantics. Incomplete graph data must not lower verification or broaden authorization.

**Choice:** Add an optional `graph_impact` section to `RoutingPolicy`. The closed effect vocabulary is `open`, `review` and `blocked` for the gate; `standard`, `elevated` and `strict` for verification; `prefer`, `neutral`, `demote`, `exclude` and `unresolved` for candidate selection. The default policy is transitive impact with `max_depth=4`, `max_nodes=256`, `max_edges=1024`, unresolved candidate evidence using static ordering, and incomplete graph evidence using at least elevated verification. The effective routing result is monotonic: gate severity, verification depth and required roles are merged by conservative rank; graph effects cannot downgrade A or B state.

**Rationale:** Policy remains inspectable data, while composition is deterministic code. Existing callers can omit graph inputs and retain existing A/B behavior. Explicit graph evidence may prefer or constrain a candidate; absent evidence cannot grant eligibility.

**Alternatives Rejected:**
1. Replace complexity with a weighted graph score - rejected because A's tested risk semantics would be lost.
2. Treat unresolved as neutral - rejected because incomplete evidence could silently reduce verification.

**Consequences:**
- Policy tests must cover every configured effect and the merge ordering.
- A graph policy change changes assessment and decision identities by design.

---

### Decision 4: Candidate mapping is caller-supplied and evidence-first

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-25 |

**Context:** The current graph vocabulary has no generic capability node, and adding inferred capability nodes would couple graph construction to runtime registry state. Selection still needs a safe way to use explicit graph relationships when available.

**Choice:** Add optional `graph_candidate_refs: Mapping[candidate_name, tuple[node_id, ...]]` to `RoutingRequest`. The caller supplies only IDs backed by an explicit local graph relationship. A candidate is graph-matched when one of its references is in the target's bounded impacted set or is the target itself. Candidates without references are marked `unresolved` for graph selection and retain the static A/B order. No candidate becomes eligible solely because it appears in the graph; existing profile, risk, evidence and expertise checks still apply.

**Rationale:** This enables graph-aware selection without inventing a new node kind or silently coupling the graph builder to registry internals. It also gives capability owners an explicit, reviewable mapping in fixtures and request artifacts.

**Alternatives Rejected:**
1. Match by capability name or substring - rejected because names are not graph evidence and can collide.
2. Add a new capability graph node kind in the MVP - rejected because it expands the graph contract and builder scope before the assessment is proven.

**Consequences:**
- Callers that want graph-aware selection must provide explicit candidate references.
- Unmapped candidates remain safe and explainable, but they do not receive a graph preference.

---

### Decision 5: One stored assessment feeds all projections

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-09-25 |

**Context:** The same impact explanation must be visible in routing, governance and capability-owner experiences while avoiding projection-specific recomputation.

**Choice:** Persist `graph_impact` on `RoutingDecision`; copy only the resulting gate/evidence/unresolved values to `RoutingPlan`, and pass the decision payload through existing runtime and brief projections. Add a standalone `graph-impact.json` only when the existing run store needs a direct artifact lookup; its bytes must be exactly the serialized assessment already embedded in the decision.

**Rationale:** This creates one lineage path from graph snapshot to user-visible brief and keeps the plan contract focused on execution roles. It also makes replay and artifact comparison straightforward.

**Alternatives Rejected:**
1. Re-run graph traversal while rendering a brief - rejected because the brief could differ from the executed route.
2. Put graph paths only in logs - rejected because logs are not a versioned evidence contract.

**Consequences:**
- Projection tests must assert identity and payload equality, not merely the presence of a summary string.
- Existing consumers must tolerate a missing optional `graph_impact` field.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/apiforge/contracts/graph_impact.py` | Create | Define `GraphImpactPolicy`, effect, node, candidate and `GraphImpactAssessment/v1` contracts plus defaults | @python-developer | None |
| 2 | `src/apiforge/contracts/routing.py` | Modify | Add optional graph target/mode/candidate refs to `RoutingRequest`, graph assessment to `RoutingDecision`, and additive graph evidence to `RoutingPlan` if required by implementation | @python-developer | 1 |
| 2a | `src/apiforge/contracts/task.py` | Modify | Carry the stored graph assessment through `OutcomeBrief/v1` for the explainable brief projection | @python-developer | 1 |
| 3 | `src/apiforge/contracts/__init__.py` | Modify | Export graph impact contracts | @python-developer | 1 |
| 4 | `src/apiforge/contracts/registry.py` | Modify | Register versioned graph impact contracts for validation and artifact discovery | @python-developer | 1 |
| 5 | `src/apiforge/graph/impact.py` | Create | Implement pure bounded reverse traversal, canonical ordering, coverage classification and candidate matching | @python-developer | 1 |
| 6 | `src/apiforge/graph/__init__.py` | Modify | Export the public graph impact assessor without changing the store boundary | @python-developer | 5 |
| 7 | `src/apiforge/runtime/routing.py` | Modify | Load policy, invoke one assessment, merge graph effects monotonically, alter explicit candidate ordering and include graph data in decision identity | @python-developer | 1, 2, 5 |
| 8 | `src/apiforge/runtime/supervisor.py` | Modify | Load verified local graph snapshot when requested and pass typed graph data into routing; retain offline boundary | @python-developer | 5, 7 |
| 9 | `src/apiforge/runtime/store.py` | Modify | Persist/load the canonical graph impact artifact if the run-store seam needs direct lookup | @python-developer | 1 |
| 10 | `src/apiforge/runtime/runner.py` | Modify | Validate and expose optional graph-impact artifact with the existing run result projection | @python-developer | 9 |
| 11 | `src/apiforge/application/runtime_experience.py` | Modify | Surface the stored graph assessment to runtime and governance experience payloads without recomputation | @code-documenter | 2, 7, 9 |
| 12 | `src/apiforge/brief/render.py` | Modify | Add an explainable graph impact section to the existing brief projection | @code-documenter | 1, 7 |
| 13 | `src/apiforge/rules/agentic_runtime.yaml` | Modify | Add versioned default graph impact policy under `runtime.routing.graph_impact` | (general) | 1, 7 |
| 14 | `docs/contracts/GraphImpactPolicy-v1.md` | Create | Document policy fields, closed effect vocabulary and defaults | @code-documenter | 1, 13 |
| 15 | `docs/contracts/GraphImpactAssessment-v1.md` | Create | Document assessment schema, identity, provenance and unresolved semantics | @code-documenter | 1, 5 |
| 15a | `docs/contracts/GraphImpactEffect-v1.md` | Create | Document the closed monotonic gate, verification and selection effect | @code-documenter | 1 |
| 15b | `docs/contracts/GraphImpactNode-v1.md` | Create | Document explicit impacted-node provenance and ordering | @code-documenter | 1, 5 |
| 15c | `docs/contracts/GraphCandidateImpact-v1.md` | Create | Document caller-supplied candidate mapping and safe selection effect | @code-documenter | 1, 5 |
| 16 | `docs/contracts/RoutingRequest-v1.md` | Modify | Document optional graph target/mode/candidate-reference inputs and compatibility | @code-documenter | 2 |
| 17 | `docs/contracts/RoutingDecision-v1.md` | Modify | Document embedded canonical assessment and monotonic gate composition | @code-documenter | 2, 7 |
| 18 | `docs/contracts/RoutingPlan-v1.md` | Modify | Document graph-derived evidence, gate and unresolved projection | @code-documenter | 2, 7 |
| 18a | `docs/contracts/OutcomeBrief-v1.md` | Modify | Document the optional canonical graph assessment in runtime briefs | @code-documenter | 2a, 12 |
| 19 | `tests/graph/test_impact.py` | Create | Unit-test direct, transitive, all, order, cycle, depth, node/edge budget and unresolved behavior | @test-generator | 1, 5 |
| 20 | `tests/contracts/test_graph_impact.py` | Create | Test validation, defaults, stable serialization and closed policy vocabularies | @test-generator | 1 |
| 21 | `tests/runtime/test_routing.py` | Modify | Test graph-aware gate, explicit candidate selection, A/B compatibility and decision replay | @test-generator | 2, 5, 7 |
| 22 | `tests/runtime/test_routing_plan.py` | Modify | Test monotonic plan gate, required roles, evidence and unresolved propagation | @test-generator | 2, 7 |
| 23 | `tests/application/test_runtime_experience.py` | Modify | Test runtime/governance/capability-owner projections consume the stored assessment | @test-generator | 9, 11, 12 |
| 23a | `tests/contracts/test_conformance.py` | Modify | Preserve existing brief validation and prove graph assessment round-trip | @test-generator | 2a, 18a |
| 24 | `tests/fixtures/workspaces/graph_impact_cases.yaml` | Create | Canonical graph fixtures for direct, transitive, all, cycle, cutoff, stale and missing evidence cases | (general) | None |
| 25 | `tests/fixtures/workspaces/graph_impact_expected.yaml` | Create | Expected assessment, gate, order and projection outputs for each fixture | (general) | 24 |
| 26 | `tests/evals/cases/graph_aware_impact.yaml` | Create | Offline evaluation cases covering AT-001 through AT-011 | @test-generator | 24, 25 |
| 27 | `tests/evals/test_graph_aware_impact.py` | Create | Execute the evaluation cases and assert no external integration is invoked | @test-generator | 5, 7, 26 |

**Total Files:** 33

The Build phase may omit file 9 or 10 if existing routing serialization already exposes the embedded assessment directly; if it does, the omission must be documented in the implementation result and the acceptance tests must still verify direct artifact replay. No file outside this manifest may be changed without updating the design or recording a build-time scope exception.

---

## Agent Assignment Rationale

> Agents discovered from `C:\Users\edgar\.codex\plugins\cache\agentspec\agentspec\3.6.0\agents/` - Build phase invokes matched specialists.

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @python-developer | 1-10, 19-22 | Python contracts, pure graph traversal, runtime routing and typed integration are the primary implementation surface |
| @test-generator | 19-23, 26-27 | Fixture-driven unit, integration and evaluation coverage is required for every acceptance test |
| @code-documenter | 11-12, 14-18 | The projection and contract documentation must expose the same evidence and unresolved semantics |
| (general) | 13, 24-25 | Policy YAML and canonical expected-output fixtures require repository-specific judgment rather than a narrower specialist |

**Agent Discovery:**
- Scanned: `C:\Users\edgar\..codex\plugins\cache\agentspec\agentspec\3.6.0\agents/**/*.md`
- Matched by: Python contract/runtime files, graph/traversal purpose, fixture/evaluation testing, documentation and policy paths.
- Available matching specialists: `python/python-developer.md`, `test/test-generator.md`, `python/code-documenter.md`.
- No dedicated graph-impact specialist was present; graph-specific work remains assigned to the Python specialist with repository-local tests as the authority.

---

## Code Patterns

### Pattern 1: Immutable versioned assessment contracts

```python
from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract
from apiforge.contracts.graph import GraphExport, NodeKind


class GraphImpactNode(VersionedContract):
    node_id: str = Field(min_length=1)
    kind: NodeKind
    depth: int = Field(ge=0)
    edge_refs: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()


class GraphImpactAssessment(VersionedContract):
    assessment_id: str
    target_id: str
    target_kind: NodeKind | None = None
    mode: Literal["direct", "transitive", "all"]
    policy_version: str
    graph_snapshot: GraphExport | None = None
    coverage: Literal["complete", "partial", "missing", "unresolved"]
    freshness_state: Literal["fresh", "stale", "unresolved", "unknown"]
    impacted_nodes: tuple[GraphImpactNode, ...] = ()
    evidence: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    gate_state: Literal["open", "review", "blocked"] = "open"
    verification_depth: Literal["standard", "elevated", "strict"] = "standard"
```

The actual implementation may split policy, candidate and effect models into the same module, but every nested sequence must be tuple-based and sorted before construction. The `assessment_id` is calculated from a separate canonical payload so identity never hashes itself.

### Pattern 2: Pure bounded traversal with stable ordering

```python
from collections import deque

from apiforge.contracts.graph import GraphEdge, GraphNode


def reverse_impact(
    nodes: tuple[GraphNode, ...],
    edges: tuple[GraphEdge, ...],
    target_id: str,
    *,
    max_depth: int,
    max_nodes: int,
    max_edges: int,
) -> tuple[tuple[str, int, tuple[str, ...]], tuple[str, ...]]:
    known = {node.id: node for node in nodes}
    adjacency: dict[str, list[tuple[str, str]]] = {}
    for edge in sorted(edges, key=lambda item: (item.to_id, item.from_id, item.kind.value)):
        adjacency.setdefault(edge.to_id, []).append((edge.from_id, edge.kind.value))

    queue: deque[tuple[str, int]] = deque([(target_id, 0)])
    seen: dict[str, int] = {}
    edge_refs: dict[str, set[str]] = {}
    limitations: set[str] = set()
    traversed_edges = 0
    while queue:
        current, depth = queue.popleft()
        if depth >= max_depth:
            if adjacency.get(current):
                limitations.add(f"max_depth:{current}:{max_depth}")
            continue
        for source_id, edge_kind in adjacency.get(current, ()):
            if traversed_edges >= max_edges:
                limitations.add(f"max_edges:{max_edges}")
                return _ordered_nodes(seen, edge_refs), tuple(sorted(limitations))
            traversed_edges += 1
            ref = f"{source_id}->{edge_kind}->{current}"
            if source_id not in known:
                limitations.add(f"missing_node:{source_id}")
                continue
            edge_refs.setdefault(source_id, set()).add(ref)
            if source_id == target_id:
                limitations.add(f"cycle:{source_id}")
                continue
            if source_id not in seen:
                if len(seen) >= max_nodes:
                    limitations.add(f"max_nodes:{max_nodes}")
                    return _ordered_nodes(seen, edge_refs), tuple(sorted(limitations))
                seen[source_id] = depth + 1
                queue.append((source_id, depth + 1))
    return _ordered_nodes(seen, edge_refs), tuple(sorted(limitations))
```

The snippet shows the required boundary behavior, not a replacement for the repository's final helper names. Build must keep missing-node, cycle and budget diagnostics explicit and must never use a set's iteration order as output order.

### Pattern 3: Monotonic policy composition

```python
_GATE_RANK = {"open": 0, "review": 1, "blocked": 2}
_DEPTH_RANK = {"standard": 0, "elevated": 1, "strict": 2}


def merge_graph_effect(
    risk_gate: str,
    risk_depth: str,
    risk_roles: tuple[str, ...],
    graph_gate: str,
    graph_depth: str,
    graph_roles: tuple[str, ...],
) -> tuple[str, str, tuple[str, ...]]:
    gate = risk_gate if _GATE_RANK[risk_gate] >= _GATE_RANK[graph_gate] else graph_gate
    depth = risk_depth if _DEPTH_RANK[risk_depth] >= _DEPTH_RANK[graph_depth] else graph_depth
    roles = tuple(sorted(set(risk_roles) | set(graph_roles)))
    return gate, depth, roles
```

If an unresolved graph effect is configured as `blocked`, that choice is honored. If it is configured as `elevated`, it still cannot lower an existing `strict` or `blocked` result. The merge must be covered by boundary tests for every rank combination.

### Pattern 4: Policy structure

```yaml
runtime:
  routing:
    graph_impact:
      policy_version: graph-impact/v1
      default_mode: transitive
      max_depth: 4
      max_nodes: 256
      max_edges: 1024
      incomplete_effect: elevated
      unknown_candidate_effect: unresolved
      effects:
        none:
          gate_state: open
          verification_depth: standard
          required_roles: []
          selection: neutral
        explicit:
          gate_state: review
          verification_depth: elevated
          required_roles: [reviewer]
          selection: prefer
        bounded:
          gate_state: review
          verification_depth: strict
          required_roles: [reviewer, critic]
          selection: prefer
        unresolved:
          gate_state: review
          verification_depth: elevated
          required_roles: [reviewer]
          selection: unresolved
```

The parser must validate the YAML through the Pydantic policy contract and reject unknown effect values with the existing `AF-RUNTIME-POLICY` boundary. The build may choose equivalent names, but it must retain a closed, documented vocabulary and deterministic defaults.

---

## Data Flow

```text
1. The caller creates the existing RoutingRequest. Graph-aware callers add an explicit target,
   mode and candidate-to-node references; legacy callers leave them absent.
   │
   ▼
2. The supervisor loads the local graph JSONL through read_graph(), verifies node hashes and
   associates the GraphExport/v1 snapshot plus declared freshness/evidence references.
   │
   ▼
3. The pure assessor validates the target, traverses explicit reverse edges within policy
   bounds, records nodes/edge refs/limitations, classifies coverage and computes assessment_id.
   │
   ▼
4. Routing runs existing A risk/complexity and candidate eligibility, merges the graph effect
   monotonically, and ranks only where explicit candidate references provide graph evidence.
   │
   ▼
5. B scorecard routing and offline shadow evaluation run on the graph-aware candidate order;
   the RoutingDecision identity includes the canonical graph assessment.
   │
   ▼
6. RoutingPlan copies effective gate/evidence/unresolved values and keeps role disjointness and
   fallback bounds. RunStore persists the decision, plan and optional standalone assessment.
   │
   ▼
7. Runtime, governance and capability-owner projections render the stored assessment, including
   impacted nodes, explicit paths, policy effect, freshness and unresolved gaps.
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|------------------|----------------|
| Local graph JSONL store | Existing file adapter (`read_graph`) | None; local filesystem only |
| Existing case/API-IR/facts/findings artifacts | Existing deterministic graph builder and evidence references | None |
| Runtime routing supervisor | In-process typed function call | None |
| RunStore JSON artifacts | Existing local serialization | None |
| Provider APIs, live deployment graph, traffic graph, database or model SDK | Explicitly not integrated in MVP | Not applicable; boundary remains read-only/offline |

No new external system, credential, network client or mutation path is introduced.

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Contract unit | Pydantic validation, defaults, closed literals, stable dumps and identity inputs | `tests/contracts/test_graph_impact.py` | pytest | 100% of contract validators and default policy branches |
| Graph unit | Reverse traversal, canonical order, direct/transitive/all modes, cycles, depth/node/edge bounds, missing target/node and freshness | `tests/graph/test_impact.py` | pytest + fixture factories | Every branch in AT-001 through AT-006 |
| Routing integration | A/B compatibility, monotonic gate merge, explicit candidate preference, unresolved fallback, scorecard and shadow order | `tests/runtime/test_routing.py`, `tests/runtime/test_routing_plan.py` | pytest | AT-007, AT-008, AT-010 |
| Projection integration | Identity/payload equality across runtime, governance and capability-owner projections; no second traversal | `tests/application/test_runtime_experience.py` | pytest, monkeypatch assessor to fail if called | AT-009 |
| Fixture evaluation | Expected artifacts for all supported `NodeKind` values represented by existing fixtures and all failure states | `tests/evals/cases/graph_aware_impact.yaml`, `tests/evals/test_graph_aware_impact.py` | existing offline eval harness | AT-001 through AT-011, 100% deterministic replay |
| Offline boundary | Assert no provider/network/database/model SDK or graph mutation is used | `tests/evals/test_graph_aware_impact.py` | monkeypatch/deny-list plus local temp directories | Zero external calls in MVP |
| Repository gates | Formatting, lint, typing, full regression and SDD contract check | existing CI commands | `pytest`, `ruff`, `mypy`, `apiforge sdd check`, spec-linter | No regression; all mandatory gates pass |

Required acceptance mapping:

| Acceptance | Primary proof |
|------------|---------------|
| AT-001 | Same fixture twice, compare full `model_dump(mode="json")` and IDs |
| AT-002 to AT-004 | Parametrized fixture cases for direct, transitive and all |
| AT-005 | Cycle and each budget bound terminate with sorted limitation |
| AT-006 | Stale/missing/unresolved fixture asserts conservative effect and visible gap |
| AT-007 | Routing plan asserts max(risk, graph) gate/depth/roles |
| AT-008 | Candidate refs alter order only with explicit matching evidence |
| AT-009 | Projections compare embedded assessment ID and serialized payload |
| AT-010 | Existing routing tests plus request with no graph fields are unchanged |
| AT-011 | External adapters are denied and no calls are observed |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Graph directory or `nodes.jsonl` missing | Return a named `AF-GRAPH-NOT-FOUND`/unresolved assessment when graph impact was requested; use policy incomplete effect; preserve routing artifact | No automatic retry; provide local graph artifact |
| Node hash mismatch or malformed graph row | Preserve the existing `AF-GRAPH-HASH-MISMATCH`/`AF-GRAPH-INVALID` error at the adapter boundary; do not route with unverified graph data | No; repair or regenerate the local graph |
| Target absent from graph | Return `coverage=missing`, `unresolved` target evidence and policy fallback; do not infer a target | No; provide the explicit target node |
| Edge points to missing node | Keep valid evidence, record `missing_node` limitation and apply incomplete policy | No; repair graph evidence |
| Max depth/nodes/edges reached | Return bounded partial assessment with deterministic limitation; never continue beyond the configured budget | No; increase policy only explicitly |
| Invalid graph impact policy | Raise `ContractError` with `AF-RUNTIME-POLICY`, rejected field and safe unlock before routing | No; fix versioned local policy |
| Candidate mapping absent or points to unknown node | Mark candidate graph state `unresolved`; retain static A/B eligibility and conservative order | No; provide explicit graph refs |
| Projection artifact missing | Preserve routing result with `routing_errors`/unresolved evidence; do not recalculate impact in the projection | No; restore or rerun local artifact |

All refusals retain the existing `AF-*` code, rejected field and safe unlock. No error path silently converts `unresolved` to `open` or grants an otherwise ineligible capability.

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `runtime.routing.graph_impact.policy_version` | string | `graph-impact/v1` | Version included in policy and assessment identity |
| `runtime.routing.graph_impact.default_mode` | enum | `transitive` | Impact scope when the request asks for graph impact but omits a mode |
| `runtime.routing.graph_impact.max_depth` | int | `4` | Maximum reverse traversal depth |
| `runtime.routing.graph_impact.max_nodes` | int | `256` | Maximum unique impacted nodes |
| `runtime.routing.graph_impact.max_edges` | int | `1024` | Maximum traversed explicit edges |
| `runtime.routing.graph_impact.incomplete_effect` | enum | `elevated` | Minimum effect for stale, missing, partial or unresolved graph evidence |
| `runtime.routing.graph_impact.unknown_candidate_effect` | enum | `unresolved` | How candidates without explicit graph mapping are represented; never an eligibility grant |
| `runtime.routing.graph_impact.effects` | mapping | documented policy table | Gate, verification, required-role and selection effects for `none`, `explicit`, `bounded` and `unresolved` states |

Request-level `graph_target`, `graph_mode` and `graph_candidate_refs` are optional and are not environment variables. The graph directory is supplied by the existing run/case context; the feature does not accept a remote URI.

---

## Security Considerations

- Treat graph nodes, edge properties and evidence references as untrusted local data: validate closed kinds, verify node hashes and never execute values found in graph properties.
- Preserve the existing eligibility gate. A graph match can influence ordering or add review requirements, but it cannot make a disabled, unsupported, risk-incompatible or evidence-incomplete capability eligible.
- Treat stale, incomplete, missing and unresolved states as safety-relevant. Policy composition is monotonic, so these states cannot reduce verification depth or broaden authorization.
- Keep traversal bounded by policy and use stable identity/sorting to prevent resource-exhaustion and replay ambiguity from adversarial graph input.
- Do not add provider credentials, network clients, database access, model SDK calls or graph mutation to the assessment or projection layers.
- Do not serialize secrets from graph properties into briefs; evidence references are identifiers only and existing redaction/serialization boundaries remain authoritative.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Add structured routing event fields for `assessment_id`, `target_id`, `mode`, `coverage`, `freshness_state`, `impacted_count`, policy effect and unresolved count; do not log full arbitrary graph props |
| Metrics | Keep deterministic local counters in the routing/result artifact for impacted nodes, traversed edges, budget cutoffs and unresolved candidates; no production TPS/latency claim is introduced |
| Tracing | Reuse existing routing decision and run event IDs; reference the assessment ID and graph snapshot hashes instead of adding an external tracing dependency |

Observability values are derived from the persisted assessment and are therefore replayable. A projection must not report an impact count that differs from the canonical assessment.

---

## Pipeline Architecture (if applicable)

This feature is not an ETL, analytics or streaming pipeline. The closest applicable flow is the bounded local assessment pipeline described below; it does not create tables, partitions or incremental models.

### DAG Diagram

```text
[Graph JSONL + GraphExport] ──validate──→ [Bounded Impact Assessment]
          + RoutingRequest ──────────────↗             │
                                                     ├──→ [Gate/Selection]
                                                     └──→ [Stored Brief]
```

### Partition Strategy

| Table | Partition Key | Granularity | Rationale |
|-------|---------------|-------------|-----------|
| Not applicable | Not applicable | Not applicable | MVP is local JSON/JSONL and has no analytical table |

### Incremental Strategy

| Model | Strategy | Key Column | Lookback |
|-------|----------|------------|----------|
| Not applicable | Recompute only when canonical graph/request/policy identity changes | `assessment_id` | None |

### Schema Evolution Plan

| Change Type | Handling | Rollback |
|-------------|----------|----------|
| New assessment field | Add optional field with deterministic default, then document in the versioned contract | Read prior `GraphImpactAssessment/v1` with compatibility default |
| Semantic effect change | Bump policy version and assessment contract only when the shape changes; retain old policy parser during migration | Restore prior policy version |
| Field removal | Deprecate in contract and projection before removal; do not drop evidence silently | Re-enable the field and rerun local assessment |

### Data Quality Gates

| Gate | Tool | Threshold | Action on Failure |
|------|------|-----------|-------------------|
| Canonical replay | pytest/evaluation fixture | 100% identical assessment bytes for identical inputs | Block build |
| Evidence preservation | contract/evaluation assertions | 0 dropped node, edge, source or unresolved refs | Block build |
| Bound compliance | graph unit tests | 0 traversals beyond configured depth/node/edge budget | Block build |
| Offline boundary | deny-list/monkeypatch test | 0 external calls or graph mutations | Block build |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-25 | design-agent | Initial technical design from the approved Graph-Aware Impact DEFINE |
| 1.1 | 2026-09-25 | build-agent | Implemented the 33-file manifest, added OutcomeBrief propagation and registered nested contract documentation |

---

## Next Step

**Ready for:** `/ship .claude/sdd/features/DEFINE_GRAPH_AWARE_IMPACT.md`
