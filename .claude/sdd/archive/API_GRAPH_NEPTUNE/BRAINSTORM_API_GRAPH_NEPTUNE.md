# BRAINSTORM: API Graph & Neptune Specialization

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_GRAPH_NEPTUNE |
| **Date** | 2026-10-01 |
| **Author** | brainstorm-agent |
| **Status** | ✅ Complete (Defined) |

---

## Initial Idea

**Raw Input:** `prompt_evo_api_graph_neptune.md` — assessment of `main@4ebd286`: API Forge is strong on
*system graph* (graph contracts, impact, workspace graph, cross-repo inference), supports Neptune
explicitly via `api-data-access-architect`, but has no dedicated graph-database specialist and no deep
Graph Database Engineering (modeling, Gremlin/openCypher/SPARQL query engineering, plans, Neptune ops).
Proposal: a vendor-neutral graph data specialization with Neptune as a vendor pack, able to connect the
software's own graph with business/data graphs.

**Context Gathered:**
- Static Neptune extractor exists: `src/apiforge/adapters/dbaccess.py:61-326` — Python AST for
  `execute_gremlin_query` / `execute_open_cypher_query` / `execute_sparql`, Java/Go regex; `unbounded`
  is a same-line `.limit(`/`.range(` heuristic (multi-line chains stay conservatively unbounded).
- Governance: `src/apiforge/data_governance.py:29,105-117` — Gremlin mutation tokens
  (`addv/adde/drop/addvertex/addedge`) and a binary `unbounded-graph-traversal` risk.
- Posture: `collect neptune` → `model neptune` (`src/apiforge/adapters/awsdumps.py`, `collectors/datastores.py`).
- System-graph export `--format neptune` is a **named stub** (`src/apiforge/graph/export.py:18`,
  `contracts/graph.py:115`) — OpenCSV planned, not implemented.
- Prior SDD `docs/sdd/API_FORGE_GRAPH_DOCUMENT_SPECIALIZATION_7` shipped document/graph profiles and
  bounded-query risk; explicitly out of scope: `explain-live`, `index-creation`, `graph-mutation`.
- `agents/api-data-access-architect.md:15` declares "query plans and cardinality are blind spots".
- Agent roster was just consolidated 52→25 (`sdd/agent-roster`) → any new agent must justify itself
  against redundancy.
- Only one graph fixture in repo: `tests/fixtures/dbaccess_app/neptune_repo.py`.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/apiforge/adapters/` (new `graph_/` module), `src/apiforge/contracts/`, `src/apiforge/collectors/`, `src/apiforge/graph/export.py`, `agents/`, `.agents/skills/api-forge-graph/` | Follows extractor → IR → governance → CLI/MCP pattern of prior specializations |
| Relevant KB Domains | agentspec KB has **no graph domain**; tangential: `data-modeling`, `aws`, `testing`, `anti-patterns`, `component-model` | Graph knowledge lives in the new skill references/packs (source: AWS Neptune, Apache TinkerPop, openCypher, W3C SPARQL 1.1, Neo4j docs) |
| IaC Patterns | N/A — core is offline; no provider SDK in `src/` | Collector stays outside core, GET-only with receipt |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Primary goal: graph DB engineering, Neptune depth only, system↔domain graph bridge, or all? | **All of the above** | Multi-wave program covering the three layers (system graph, domain graph, graph database) |
| 2 | Evidence boundary for graph query analysis? | **Offline imported dumps + optional GET-only collector** | `model graph-explain` parses operator-imported plans; `collect neptune-explain` added outside core; core stays offline |
| 3 | How to materialize the specialist in the roster? | **"As complete as possible, best quality, without redundancy"** | Ownership must be exclusive: one graph agent + skill with vendor packs; transversal concerns stay with existing agents |
| 4 | How to prove completeness/quality? | **Golden query corpus + explain/profile fixtures + field cycle + export round-trip** | Four independent verifiers; eval suite `graph-quality` |
| 5 | Which real samples exist? | **Explain/profile outputs and cluster dumps** (owner has them) | Shapes are known to exist in the field |
| 6 | Where are the samples? | **Synthesize look-alikes** from official docs | Fixtures marked `synthetic`; replacement by redacted real outputs is a pre-ship gap |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files (code) | `tests/fixtures/dbaccess_app/neptune_repo.py` | 1 | Only existing graph fixture; golden corpus must be authored (Py/Java/Go/TS, Neptune + Neo4j, good + bad) |
| Output examples (plans) | To be synthesized under `tests/fixtures/graph_explain/` | 0 → N | Neptune Gremlin explain/profile, openCypher explain static/dynamic, SPARQL explain, Neo4j EXPLAIN/PROFILE; shapes from official docs; tagged `synthetic` |
| Output examples (posture) | To be synthesized from `collect neptune` shape | 0 → N | Cluster dumps (describe-db-clusters, instances, parameter groups, CloudWatch) |
| Ground truth | Official specs: Neptune bulk loader CSV format, RDF N-Triples, TinkerPop step semantics | — | Export round-trip and rule expectations validate against spec, not opinion |
| Related code | `adapters/dbaccess.py`, `data_governance.py`, `adapters/awsdumps.py`, `graph/export.py`, `contracts/graph.py` | 5 | Patterns to extend, not duplicate |

**How samples will be used:**
- Golden corpus → `apiforge evals graph-quality` precision/recall per `AF-GRAPH-*` rule.
- Plan fixtures → parser tests + plan-rule tests for `GraphPlanIR`.
- Spec ground truth → export round-trip validation (OpenCSV, N-Triples).
- Owner's real (redacted) explain/profile outputs and dumps → replace synthetic fixtures before ship.

---

## Approaches Explored

### Approach A: One graph specialist + skill with vendor packs, no Neptune agent ⭐ Recommended

**Description:** New vendor-neutral agent `api-graph-data-architect` owns every graph-store question
(modeling, query languages, traversal anti-patterns, plan reading, graph-store posture, system-graph
export to graph DBs). New skill `api-forge-graph` with vendor-neutral references and `packs/neptune`,
`packs/neo4j`. `api-data-access-architect` cedes `model neptune-access` / `model neptune` and routes graph
stores to the new agent. IAM/VPC, topology, CloudWatch monitors and failure handling stay with the
existing owners.

**Pros:**
- Covers all three layers; roster grows by one (25→26).
- Exclusive ownership → no redundancy with infra-reviewer, architecture-reviewer, observability, resilience.
- New vendors (beyond Neptune/Neo4j) become packs, never new agents.

**Cons:**
- One agent with a wide scope (modeling + Neptune ops posture).
- Skill must be well segmented so packs load on demand and do not bloat context.

**Why Recommended:** Codebase precedent (confidence 0.80, no KB match): prior specializations shipped
as one agent per domain + skill + extractor + governance rules (e.g. `api-event-driven-architect` +
`api-forge-messaging`/`api-forge-streaming`). A Neptune-only agent would duplicate four existing owners.

---

### Approach B: Two agents (graph + Neptune)

**Description:** Approach A plus `api-neptune-engineer` owning Neptune AWS operations and cost.

**Pros:**
- Explicit owner for Neptune operations.

**Cons:**
- Overlaps `api-infra-reviewer` (IAM/VPC), `api-architecture-reviewer` (topology),
  `api-observability-*` (CloudWatch), `api-operations-engineer`.
- Vendor-per-agent contradicts the 52→25 consolidation; Neo4j would demand a third agent.

---

### Approach C: No new agent — extend `api-data-access-architect` + skill

**Description:** Same skill/code as A, absorbed by the existing data-access agent.

**Pros:**
- Roster stays at 25; no routing change.

**Cons:**
- Agent already spans nine stores; RDF modeling, plan reading and the system↔domain bridge do not fit
  "what the code does to its data stores".
- Overloaded "Use when…" description degrades routing quality.

---

## Data Engineering Context (if applicable)

### Source Systems
| Source | Type | Volume Estimate | Current Freshness |
|--------|------|-----------------|-------------------|
| Application code | Gremlin / openCypher / SPARQL call sites (Neptune, Neo4j) | per repo | static scan |
| Plan dumps | Operator-imported explain/profile output | per query | operator-run |
| Neptune explain endpoints | GET-only collector (optional) | per query | on demand, receipted |
| Cluster dumps | `collect neptune` | per cluster | operator-run |
| API Forge system graph | `graph export` | per workspace | on demand |

### Data Flow Sketch
```text
[code] ──extract──► GraphAccessIR ──AF-GRAPH rules──► findings ─┐
   │                     │                                      │
   │                     └──► inferred DomainGraph (labels/edges)│
[plan dump | collect neptune-explain] ─► GraphPlanIR ─► plan rules ┤
[collect neptune] ─► posture model ─────────────────────────────────┤
[system graph] ─► export (Neptune OpenCSV | RDF N-Triples) ─────────┘
                                                   ▼
                              api-graph-data-architect (skill + packs)
```

### Key Data Questions Explored
| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Can the core connect to Neptune? | No — offline core; collector outside core, GET-only, receipted | Plans enter as dumps or collector receipts |
| 2 | May PROFILE (which executes the query) run? | Yes, opt-in only, guarded | Mutation detector + explicit flag + declared reader endpoint, else `AF-GRAPH-PROFILE-*` refusal |
| 3 | Who consumes output? | Agents (CLI/MCP), humans via findings and evals | Every refusal keeps `AF-*` code, `field`, `unlock` |

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-10-01 (explicit selection "A (Recomendada)") |
| **Reasoning** | Most complete coverage at best quality without redundant ownership |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Single `api-graph-data-architect`, vendor-neutral | Exclusive ownership of graph stores; vendors are packs | `api-neptune-engineer` (duplicates infra/architecture/observability owners) |
| 2 | `api-data-access-architect` cedes Neptune tools | Zero overlap in routing | Shared ownership |
| 3 | Skill `api-forge-graph` with `references/` + `packs/neptune`, `packs/neo4j` | On-demand loading; Neo4j/others extend without new agent | Knowledge inside agent body |
| 4 | New `GraphAccessIR` + `GraphPlanIR` contracts | Typed evidence for static and plan analysis; feeds inferred domain graph | Reusing generic `measures` dict only |
| 5 | Plans via imported dumps + optional GET-only collector | Keeps core offline; respects read-only adapter boundary | Live connection from core |
| 6 | Collector default = non-executing explain; PROFILE opt-in with guards | PROFILE / dynamic explain execute the query on the cluster | Unrestricted PROFILE; or no PROFILE at all |
| 7 | Neptune Analytics algorithms + vector search in scope | User kept it | Defer |
| 8 | Neo4j pack in scope (knowledge + extractor + dump parser, no collector) | User kept it; validates vendor-neutral design | Neptune-only |
| 9 | Export: Neptune OpenCSV + RDF N-Triples | Closes the existing stub; bridges system graph ↔ graph DB | Keep stub |
| 10 | Synthetic fixtures now, real redacted samples before ship | Owner chose synthesis; honesty requires the gap stays declared | Block Define on samples |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Neptune numeric cost calculator | Prices change, no ground truth; cost stays qualitative in `packs/neptune` + dump reading | Yes |
| Neo4j live collector | Not requested; Neo4j plans enter via dumps only | Yes |
| `api-neptune-engineer` agent | Redundant with existing transversal owners | No (by design) |

Proposed for removal but **kept by the owner**: Neo4j/other-vendor pack (Neo4j kept), Neptune Analytics
algorithms, executing PROFILE in the collector (kept as guarded opt-in).

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| 1. Ownership: agent, routing boundaries, skill + packs layout | ✅ | "Sim, seguir" | No |
| 2. Code surfaces: GraphAccessIR, AF-GRAPH rules, plans, collector guardrails, export | ✅ | "Sim, seguir" | No |
| 3. Waves, verifiers, declared unresolved gaps | ✅ | "Sim, gerar documento" | No |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
API Forge recognizes that code touches Neptune but cannot model, query-engineer, plan-read or export
graph data with specialist depth, and graph-store questions have no dedicated owner.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Engineers of APIs backed by Neptune/Neo4j | Unbounded traversals, supernodes, path explosion found only in production |
| API Forge agents (CLI/MCP hosts) | No owner/route for graph modeling or plan questions; "blind spots" declared |
| Architects using the system graph | Cannot load the Forge system graph into a graph DB (export stub) |

### Success Criteria (Draft)
- [ ] `api-graph-data-architect` exists in `agents/`, synced to all host mirrors, `apiforge agents lint` green; `api-data-access-architect` no longer lists `model neptune*`.
- [ ] Skill `api-forge-graph` ships `references/` (modeling, gremlin, opencypher, sparql, performance, system-graph-bridge) and `packs/neptune`, `packs/neo4j`.
- [ ] `GraphAccessIR` and `GraphPlanIR` contracts documented under `docs/contracts/` and validated by tests.
- [ ] Extraction covers Neptune + Neo4j in Python (AST) and Java/Go/TS (declared heuristic), including multi-line Gremlin chains.
- [ ] Every `AF-GRAPH-*` code is cataloged and every refusal carries `field` + `unlock` in CLI and MCP.
- [ ] Golden corpus scored by `apiforge evals graph-quality` with per-rule precision/recall thresholds set in Define.
- [ ] `model graph-explain` parses Neptune Gremlin explain/profile, openCypher explain, SPARQL explain, Neo4j EXPLAIN/PROFILE fixtures; missing plan → `unresolved`.
- [ ] `collect neptune-explain` is GET-only with receipt; PROFILE refused unless mutation-free, explicitly flagged and pointed at a declared reader.
- [ ] `graph export --format neptune` (OpenCSV) and `--format rdf` (N-Triples) round-trip against bulk-loader / N-Triples specs.
- [ ] Field cycle recorded in `apiforge field` ledger against a real graph-backed repo.
- [ ] `apiforge evals economy-hardening`, `apiforge evals agentic-quality --baseline <prev>`, `apiforge sdd check --root docs/sdd` green.

### Constraints Identified
- No provider SDK imports in `src/`; no live AWS/database mutation from the core.
- Collector lives outside core (like `collect`), GET-only, receipted; never proves freshness.
- PROFILE / dynamic explain execute queries → guarded opt-in only.
- Edit `agents/*.md` only; mirrors via `apiforge agents sync`. Edit `.agents/skills` only.
- New datastore specialization must update IR, agent routing and host mirrors (CLAUDE.md rule).
- Targeted tests per wave; full suite once before ship; pytest basetemp `E:/afpt`.
- Synthetic fixtures must be labeled `synthetic` and never reported as field evidence.

### Out of Scope (Confirmed)
- Numeric Neptune cost calculator.
- Neo4j live collector.
- Index/constraint creation and any graph mutation by API Forge (inherited from specialization 7).
- Dedicated Neptune agent.

### Proposed Waves (for Define/Design)
| Wave | Delivery | Verifier |
|------|----------|----------|
| W1 | Agent, skill + packs, routing hand-off, CLAUDE/AGENTS routing, mirrors | agents lint, skills lint, routing test |
| W2 | `GraphAccessIR`, extraction (Neptune + Neo4j, multi-language, multi-line), `AF-GRAPH-*`, inferred domain graph | golden corpus + `evals graph-quality` |
| W3 | `model graph-explain`, `GraphPlanIR`, plan rules | synthetic plan fixtures (official-doc shapes) |
| W4 | `collect neptune-explain` + PROFILE guardrails | refusal tests with mocked transport |
| W5 | Export OpenCSV + N-Triples; Neptune Analytics algo/vector rules | spec round-trip; Analytics fixtures |
| W6 | Field cycle + economy/agentic evals + SDD gate | field ledger, eval reports |

### Unresolved (carry forward)
- Real explain/profile outputs and cluster dumps exist with the owner but are not yet in the repo; until replaced (redacted), W3/W5 evidence is `synthetic-only`.
- No real graph-backed target repository identified for the field cycle → W6 blocked on owner-provided target.
- Java/Go/TS extraction remains regex heuristics, reported as diagnostics.

### KB Domains for Define
- agentspec: `data-modeling`, `aws`, `testing`, `anti-patterns`, `component-model` (tangential; no graph KB domain exists).
- Project: `.agents/skills/api-forge-data-access`, `.agents/skills/api-forge-context`, `.agents/skills/api-forge-sdd`, `docs/contracts/DataAccessReadiness-v1.md`, `docs/sdd/API_FORGE_GRAPH_DOCUMENT_SPECIALIZATION_7`.
- External ground truth: AWS Neptune user guide (explain/profile, bulk loader, Streams, Analytics), Apache TinkerPop reference, openCypher spec, W3C SPARQL 1.1 / RDF 1.1 N-Triples, Neo4j Cypher manual.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 6 discovery + 1 approach + 1 YAGNI + 3 validations |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 3 |
| Validations Completed | 3 |
| Duration | ~1 session |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_API_GRAPH_NEPTUNE.md`
