# DEFINE: Graph-Aware Impact

> A deterministic, evidence-preserving graph impact assessment that governs routing, graph-aware selection and explainable impact briefs.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | GRAPH_AWARE_IMPACT |
| **Date** | 2026-09-25 |
| **Author** | define-agent |
| **Status** | ✅ Complete (Designed) |
| **Clarity Score** | 15/15 |

---

## Problem Statement

API Forge has deterministic graph construction and bounded impact queries, but routing, governance and capability owners do not yet consume one canonical impact assessment. As a result, graph impact cannot consistently change verification depth or candidate selection while preserving explicit evidence, freshness and unresolved states.

The feature must make graph impact an additive, replayable and policy-mediated input without inferring relationships, mutating the graph or weakening the existing A risk/complexity and B scorecard evidence gates.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Runtime supervisor | Builds routing gates and execution plans | Needs impact-aware verification and selection without trusting incomplete graph state |
| Governance/evaluation owner | Reviews decisions, evidence and gaps | Needs one replayable explanation of affected nodes, paths, coverage and policy effects |
| Capability owner | Maintains specialist implementations | Needs to understand why graph evidence selected, constrained or excluded a capability |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | Produce a frozen `GraphImpactAssessment/v1` from an explicit local graph, target, impact mode and versioned policy |
| **MUST** | Preserve impacted nodes, explicit edges, depth, coverage, freshness, evidence references and unresolved diagnostics in canonical serialization |
| **MUST** | Allow the same assessment to influence verification gate, graph-aware candidate selection and explainable brief projections |
| **MUST** | Apply conservative, policy-driven fallback when graph evidence is incomplete, stale, unavailable or unresolved |
| **MUST** | Prove deterministic replay, direct/transitive/all traversal, bounded cycles/depth, evidence preservation and offline safety with fixtures and expected outputs |
| **SHOULD** | Keep A risk/complexity and B scorecard adaptation authoritative, with graph impact additive and policy-mediated |
| **SHOULD** | Preserve compatibility for callers that do not provide graph impact or use legacy routing inputs |
| **COULD** | Add a dedicated CLI/TUI view for the persisted impact assessment after the canonical artifact is stable |

**Priority Guide:**
- **MUST** = MVP fails without this (non-negotiable)
- **SHOULD** = Important, but can defer if timeline tight
- **COULD** = Nice-to-have, cut first if needed

---

## Success Criteria

Measurable outcomes (must include numbers):

- [ ] **100%** of identical graph, target, policy and input fixture replays produce identical assessment identity, gate effect, candidate order and brief payload.
- [ ] **100%** of mandatory direct, transitive, all, cycle, depth-bound and unresolved cases produce the declared expected result.
- [ ] **100%** of incomplete, stale or unresolved graph cases preserve their diagnostic and never reduce verification depth or broaden authorization without an explicit policy rule.
- [ ] **100%** of explicit impacted-node, edge, evidence and gap references survive assessment, routing, plan and brief serialization without recomputation.
- [ ] **0** provider, network, database, model SDK or graph mutation calls are introduced in the offline MVP.

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Deterministic assessment replay | The same canonical graph, target, mode, policy and input revision are provided twice | The impact assessor runs twice | `assessment_id`, impacted order, coverage, unresolved values and policy identity are identical |
| AT-002 | Direct impact | A target has explicit reverse dependents at depth one | The assessor runs in `direct` mode | Only the declared depth-one dependents are returned, in canonical order, with their edge evidence |
| AT-003 | Transitive impact | A target has a multi-hop explicit dependency chain | The assessor runs in `transitive` mode within the configured bound | All reachable dependents within the bound are returned with deterministic depth and no duplicate nodes |
| AT-004 | All impact mode | A graph contains direct and transitive dependents | The assessor runs in `all` mode | The bounded union is returned, with mode and bound preserved in the assessment |
| AT-005 | Cycle and budget safety | The graph contains a cycle or more edges than the configured traversal budget | The assessor runs | Traversal terminates deterministically, never loops, and records the bound or unresolved limitation |
| AT-006 | Incomplete graph policy | A target or relationship has missing, stale or unresolved evidence | The policy evaluates the assessment | The configured conservative effect is applied; gaps remain visible and no unsafe authorization is inferred |
| AT-007 | Graph-aware gate | A graph assessment indicates elevated or critical impact | The routing gate builds its plan | Verification depth and required roles follow the declared policy effect, while A risk/complexity remains preserved |
| AT-008 | Graph-aware selection | Candidate capabilities have explicit graph relationships to the impacted target | The route is selected | Only explicit graph evidence can influence candidate order; candidates without evidence remain unresolved or follow static fallback |
| AT-009 | Explainable projection | A canonical assessment has impacted nodes, paths, evidence and gaps | Runtime/governance/capability projections render a brief | All projections consume the same stored assessment and do not independently recalculate impact |
| AT-010 | Legacy compatibility | A caller omits graph impact and supplies existing A/B routing inputs | Routing and plan construction run | Existing selection, role disjointness, fallback bounds, risk/complexity and scorecard behavior remain valid |
| AT-011 | Offline boundary | The feature is exercised with local fixtures | The full evaluation suite runs | No provider, network, database, model SDK or graph mutation call is made |

---

## Out of Scope

Explicitly NOT included in this feature:

- Inferred dependency edges, model-generated graph relationships or heuristic links without evidence.
- Live provider, deployment, traffic or runtime graph collection.
- Graph mutation, automatic repair, index creation or graph synchronization.
- Unbounded traversal, unbounded memory growth or a new external graph database runtime.
- Replacing A risk/complexity or B scorecard adaptation with a weighted graph score.
- Automatic capability promotion, retirement or external state mutation.
- A new UI surface before the canonical assessment and projections are stable.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Use existing frozen versioned contracts, JSONL graph store, `GraphExport/v1` and explicit `NodeKind`/`EdgeKind` vocabularies | The assessment is local, typed and replayable |
| Technical | Traversal must have explicit max-depth and budget bounds | Cycles and large graphs terminate deterministically |
| Safety | Missing, stale or unresolved graph evidence cannot silently reduce verification or broaden authorization | Policy must emit conservative fallback and preserve gaps |
| Compatibility | A risk/complexity and B scorecard semantics remain authoritative | Graph impact is additive and cannot bypass existing gates |
| Evidence | Every derived impact result must point to graph/edge/source evidence or remain unresolved | The brief and route decision preserve provenance |
| Runtime | No provider SDK, network, database, model SDK or external mutation | Build and evaluation remain offline-first |
| Evaluation | Existing graph/workspace fixtures plus explicit expected outputs are mandatory | Tests prove replay, coverage, safety and compatibility |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/contracts`, `src/apiforge/graph`, `src/apiforge/context`, `src/apiforge/runtime`, `tests`, `docs/contracts` | Reuse graph construction/query, context scopes, routing and projection seams |
| **KB Domains** | `pydantic`, `python`, `testing`, `genai`; API Forge context/graph patterns | Use immutable contracts, pure bounded traversal, explicit unknown handling and fixture-driven tests |
| **IaC Impact** | None | No infrastructure, provider, database or deployment changes are required |

**Why This Matters:**

- **Location** → Design phase uses existing graph, context and routing boundaries instead of creating a parallel graph subsystem.
- **KB Domains** → Design phase can apply typed-contract, determinism, testing and guardrail patterns.
- **IaC Impact** → No deployment planning or external permission gate is triggered by the offline MVP.

---

## Data Contract (if applicable)

This feature is not an ETL or analytics pipeline, but it operates on versioned provenance artifacts and therefore has explicit source, freshness and lineage requirements.

### Source Inventory

| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| `GraphExport/v1` and local graph JSONL | Local JSON/JSONL | Bounded by policy depth/budget | Explicit artifact freshness; no production SLA | API Forge core |
| Case, API-IR, facts, findings and workspace fixtures | Local JSON/YAML | Fixture-bounded | Determined by persisted hashes and receipts | API Forge core |

### Schema Contract

| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| `assessment_id` | string | Stable hash of canonical inputs | No |
| `target_id` | string | Explicit graph node target | No |
| `mode` | enum | `direct`, `transitive` or `all` | No |
| `impacted_nodes` | tuple of typed nodes | Unique, deterministic order, bounded | No |
| `evidence` / `unresolved` | tuple of references/messages | Preserve provenance; never coerce unknown to safe | No |
| `policy_version` | string | Required in the assessment identity | No |

### Freshness SLAs

| Layer | Target | Measurement |
|-------|--------|-------------|
| Graph snapshot | No production freshness claim | Compare persisted source hashes and declared freshness state |
| Assessment | Deterministic for one graph snapshot | Recompute only when canonical input hash changes |

### Completeness Metrics

- **100%** of mandatory fixture references must survive assessment and projection.
- **0** unresolved graph diagnostics may be silently dropped.
- **100%** of traversals must respect configured depth and budget bounds.

### Lineage Requirements

- Assessment must reference the graph snapshot, target and policy version that produced it.
- Impacted nodes and edges must retain source or graph evidence references where available.
- Routing and briefs must consume the stored assessment rather than re-traversing independently.

---

## Assumptions

Assumptions that if wrong could invalidate the design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|-----------------|------------|
| A-001 | Existing JSONL graph storage and `GraphExport/v1` are the canonical local graph boundary | A new graph persistence contract would be required before implementation | [x] Existing graph contracts and builder inspected |
| A-002 | Existing bounded reverse traversal can support the MVP impact modes | A separate traversal/index design would be needed | [x] Existing `graph impact` and context impact modes inspected |
| A-003 | Candidate capabilities can be connected to impacted targets by explicit graph evidence in the required fixtures | Graph-aware selection would remain unresolved/static for candidates without those edges | [ ] Design must inspect and define the exact candidate-edge mapping |
| A-004 | Policy can express block, elevated verification and conservative static fallback effects | Safety behavior would require a new policy contract or human gate | [ ] Design must define the closed effect vocabulary and defaults |
| A-005 | Routing, plan and experience projections can carry an additive assessment without breaking A/B callers | A compatibility adapter or versioned sibling contract would be required | [x] Existing additive routing and shadow contracts provide the pattern |
| A-006 | Local fixtures can provide expected outputs for direct, transitive, all, cycle and unresolved cases | Additional verified samples would be needed before the evaluation gate | [ ] Define/build must add or confirm explicit C expected-result fixtures |

**Note:** Unvalidated assumptions are design inputs and must be resolved or explicitly preserved as gaps before Build.

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | The missing canonical impact boundary and its runtime/governance consequences are explicit |
| Users | 3 | Runtime, governance/evaluation and capability owners have distinct pain points |
| Goals | 3 | MoSCoW goals define the canonical contract, policy effects, safety and compatibility |
| Success | 3 | Replay, coverage, safety, provenance and offline criteria are measurable |
| Scope | 3 | All supported node kinds are bounded; inference, external collection and mutation are explicitly excluded |
| **Total** | **15/15** | High confidence; ready for Design |

**Scoring Guide:**
- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

No blocking questions remain for Design. Design must finalize the exact additive field shape, closed policy effect vocabulary, default depth/budget bounds, candidate-edge mapping and projection locations while preserving the requirements and unresolved assumptions above.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-25 | define-agent | Captured validated requirements from the GRAPH_AWARE_IMPACT brainstorm |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_GRAPH_AWARE_IMPACT.md`
