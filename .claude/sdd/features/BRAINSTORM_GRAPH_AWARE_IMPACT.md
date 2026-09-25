# BRAINSTORM: Graph-Aware Impact

> Exploratory session to define a canonical, deterministic graph impact assessment for routing, governance and capability selection.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | GRAPH_AWARE_IMPACT |
| **Date** | 2026-09-25 |
| **Author** | brainstorm-agent |
| **Status** | Ready for Define |

---

## Initial Idea

**Raw Input:** Start C after shipping B: combine graph-aware impact gates, graph-aware selection and an explainable impact brief, while preserving deterministic offline behavior and conservative handling of incomplete graph evidence.

**Context Gathered:**
- The repository already has `GraphExport/v1`, `WorkspaceGraph`, closed `NodeKind`/`EdgeKind` vocabularies and deterministic JSONL graph storage.
- `apiforge graph impact` performs bounded reverse traversal, while context scopes already accept `direct`, `transitive` and `all` impact modes.
- The graph builder derives nodes and edges only from explicit case, contract, API-IR, fact, finding and task artifacts; it does not infer provider or runtime dependencies.
- B shipped scorecard-adaptive routing and now has an offline shadow comparison; C must consume graph evidence without weakening A's risk/complexity or B's scorecard evidence gates.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | `src/apiforge/contracts`, `src/apiforge/graph`, `src/apiforge/context`, `src/apiforge/runtime`, `tests`, `docs/contracts` | Add a canonical assessment and pure graph evaluator at existing graph/context seams; integrate projections from that artifact |
| Relevant KB Domains | `pydantic`, `python`, `testing`, `genai`; API Forge context/graph patterns | Use frozen versioned contracts, pure bounded traversal, explicit unresolved states and fixture-driven replay tests |
| IaC Patterns | N/A | No infrastructure or provider integration is required for the offline MVP |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | What is the primary purpose of C? | Combine impact gate, graph-aware selection and an explainable brief | One assessment must serve all three outcomes; separate calculations are rejected |
| 2 | Who consumes the result? | All three: runtime supervisor, governance/evaluation and capability owners | The canonical payload must be useful for execution, audit and human explanation |
| 3 | What happens when graph evidence is incomplete, stale or unresolved? | Behavior is policy-driven by risk and impact, with conservative fallback | Unknown graph state remains visible and cannot silently lower verification or broaden authorization |
| 4 | Which samples are available? | Existing graph/workspace fixtures plus expected outputs | Reuse local fixtures and add explicit C ground truth cases before implementation |
| 5 | Which graph targets are in MVP? | All supported node types, with nodes lacking explicit evidence marked `unresolved` | Coverage is broad, but influence is limited to explicit relations and evidence |
| 6 | What defines MVP success? | Deterministic replay, conservative safety and correct graph/workspace fixture coverage | The acceptance gate must verify identity stability, no unsafe downgrade and direct/transitive behavior |

**Minimum Questions:** 3 (to ensure clarity before proceeding)

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---|---|
| Input files | `tests/fixtures/workspaces/workspace.yaml`; `.apiforge/case/{case,facts,findings,api-ir}.json` | Available tracked set | Local workspace, case, API-IR, fact and finding inputs for explicit graph construction |
| Output examples | `tests/fixtures/workspaces/expected_graph.json` | 1 known fixture | Expected graph structure and serialization reference |
| Ground truth | To be added in Define/build from the existing graph fixtures | Pending C cases | Expected impacted nodes, conservative states, route effects and brief fields will be declared explicitly |
| Related code | `src/apiforge/graph/{build,query,store}.py`; `src/apiforge/context/{resolver,scopes,service}.py`; graph/workspace/context tests | Several existing seams | Reuse traversal, scope validation, deterministic persistence and evidence projection patterns |

**How samples will be used:**

- Existing graph/workspace fixtures will ground direct, transitive and incomplete-evidence scenarios.
- `expected_graph.json` will anchor canonical node/edge identity and serialization checks.
- New expected-result cases will define impact classification, policy fallback, selection changes and explainable brief content.
- Existing case artifacts will verify provenance preservation and replay stability.

---

## Approaches Explored

### Approach A: Canonical Impact Assessment ⭐ Recommended

**Description:** Create a frozen `GraphImpactAssessment/v1` from an explicit graph snapshot, target, scope, impact mode and local policy. The same assessment drives the risk/verification gate, graph-aware candidate selection and the explainable brief.

**Pros:**
- One deterministic source of truth prevents runtime, governance and capability projections from drifting.
- Explicit evidence, freshness, depth, coverage and unresolved gaps remain auditable.
- Extends existing `GraphExport`, context scopes and bounded impact traversal without providers or graph mutation.

**Cons:**
- Requires additive contracts and integration across routing, context and projection surfaces.
- Graph-aware selection only has authority where explicit edges connect a target to a candidate; missing relationships remain unresolved.

**Why Recommended:** Codebase match plus the API Forge context skill provide strong evidence (confidence 0.95). The repository already treats graphs as deterministic provenance artifacts and already exposes bounded impact modes; a canonical assessment preserves that boundary while satisfying all three requested consumers.

---

### Approach B: Independent Graph Score

**Description:** Add a graph-derived numeric score to the existing routing ranking and use the score for selection and brief summaries.

**Pros:**
- Smaller initial integration surface.
- Can reuse existing ranking machinery.

**Cons:**
- Combines impact, quality and efficiency into an opaque scalar.
- Can hide unresolved evidence behind a number and make conservative fallback ambiguous.

**Why not recommended:** It conflicts with the project's explicit-state, evidence-aware contracts and makes the three consumers disagree about what the score means.

---

### Approach C: Post-Decision Graph Brief

**Description:** Keep routing unchanged and use the graph only after selection to produce a human-facing impact report.

**Pros:**
- Lowest regression risk for routing.
- Smallest implementation scope.

**Cons:**
- Does not provide the requested graph-aware gate or selection.
- Impact findings arrive after the runtime has already chosen a route.

**Why not recommended:** It leaves the central safety and routing problem unresolved, even though the brief itself would be useful.

---

## Data Engineering Context (if applicable)

This feature is provenance and runtime decision analysis, not an ETL, analytics or data-infrastructure pipeline.

### Source Systems

| Source | Type | Volume Estimate | Current Freshness |
|---|---|---|---|
| Local case, workspace and graph artifacts | JSON/YAML/JSONL files | Unknown; bounded by local traversal policy | Explicit artifact freshness only |

### Data Flow Sketch

```text
[GraphExport + target] → [bounded impact assessor] → [policy] → [gate/selection/brief]
```

### Key Data Questions Explored

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | What is the expected data volume? | Unknown and must remain bounded by policy | Requires max depth and traversal budget; no unbounded graph walk |
| 2 | What freshness SLA is needed? | No production SLA; artifact freshness must be explicit | Stale or absent freshness remains unresolved and cannot be treated as current |
| 3 | Who consumes the output? | Runtime, governance and capability owners | One canonical assessment must support machine and human projections |

---

## Selected Approach

| Attribute | Value |
|---|---|
| **Chosen** | Approach A — Canonical Impact Assessment |
| **User Confirmation** | 2026-09-25 |
| **Reasoning** | It satisfies the combined gate, selection and explainability goal while preserving deterministic provenance, explicit unknowns and offline safety. |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | Use one `GraphImpactAssessment/v1` for all consumers | Prevents recomputation and projection drift | Separate runtime, governance and brief assessments |
| 2 | Allow graph influence only through explicit edges and evidence | The graph builder is evidence-derived and must not infer dependencies | Heuristic or model-inferred relationships |
| 3 | Make incomplete/stale/unresolved behavior policy-driven and conservative | Risk can determine whether to block, elevate verification or use static fallback | Treat unknown graph state as zero impact or silently ignore it |
| 4 | Cover all supported node kinds but bound traversal | Broad MVP coverage is compatible with deterministic resource limits | Narrowing the MVP to routes only or allowing unbounded traversal |
| 5 | Keep the implementation local and read-only | Matches API Forge offline-first and mutation boundaries | Live provider graph, deployment or traffic integrations |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|---|---|---|
| Inferred dependency edges | No evidence source authorizes inference; it would weaken provenance | Yes, behind an explicit evidence adapter |
| Unbounded traversal | Reproducibility and resource safety require a policy budget | No; only bounded expansion should be considered |
| Live provider/deployment/traffic graph | Violates the offline core boundary and needs external receipts | Yes, as a separately governed adapter |
| Automatic graph mutation or repair | C is an assessment and decision feature, not a graph editor | Yes, with a separate mutation gate |
| New graph database or Neptune runtime | Existing JSONL graph store is sufficient for the MVP | Yes, only after measured local limits and an explicit adapter contract |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Architecture concept | ✅ | `ok` | No |
| Component breakdown | ✅ | `ok` | No |
| Data flow | ✅ | Accepted as part of the architecture/component validation | No |
| Error handling | ✅ | Policy-driven conservative fallback confirmed | Yes — unresolved state preserved explicitly |

**Minimum Validations:** 2 (to ensure alignment)

---

## Suggested Requirements for /define

Based on this brainstorm session, the following should be captured in the DEFINE phase:

### Problem Statement (Draft)

API Forge needs one deterministic, evidence-preserving graph impact assessment that can safely influence routing gates and candidate selection while producing the same explainable result for runtime and human governance consumers.

### Target Users (Draft)

| User | Pain Point |
|---|---|
| Runtime supervisor | Needs impact-aware routing and verification without trusting incomplete graph state |
| Governance/evaluation owner | Needs a replayable impact explanation with coverage, freshness and unresolved evidence |
| Capability owner | Needs to understand why a capability was selected, constrained or excluded by graph impact |

### Success Criteria (Draft)

- [ ] Identical graph, target, policy and inputs produce identical assessment, gate effect, selection and brief.
- [ ] Incomplete, stale or unresolved graph evidence never reduces verification depth or broadens authorization without an explicit policy rule.
- [ ] Existing graph/workspace fixtures cover direct, transitive, all, cycle, depth-bound and unresolved cases with expected outputs.
- [ ] All impacted-node, edge, evidence and gap provenance survives canonical serialization and projection.
- [ ] No provider, network, database or graph mutation call is introduced in the offline MVP.

### Constraints Identified

- Use frozen versioned contracts and deterministic local JSONL graph artifacts.
- Traverse only explicit edges with max-depth and budget bounds.
- Preserve `AF-*` refusals, unresolved states, evidence references and fallback explanations.
- Keep A risk/complexity and B scorecard evidence authoritative; graph impact is additive and policy-mediated.
- Validate with existing fixtures plus explicit ground-truth expected outputs.

### Out of Scope (Confirmed)

- Inferred relationships, live provider/deployment/traffic evidence and external graph mutation.
- Unbounded graph traversal or a replacement weighted scalar for risk, quality or efficiency.
- Automatic capability promotion, graph repair or a new graph database runtime.

---

## Session Summary

| Metric | Value |
|---|---|
| Questions Asked | 6 discovery questions plus sample collection |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 5 |
| Validations Completed | 2 incremental checkpoints |
| Duration | One working session on 2026-09-25 |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_GRAPH_AWARE_IMPACT.md`
