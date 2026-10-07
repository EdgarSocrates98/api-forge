# DESIGN: API Graph & Neptune Specialization

> Technical design for implementing API_GRAPH_NEPTUNE — one vendor-neutral graph-database specialist, typed graph evidence, plan reading, an allowlisted explain collector and system-graph export.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_GRAPH_NEPTUNE |
| **Date** | 2026-10-01 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_API_GRAPH_NEPTUNE.md](./DEFINE_API_GRAPH_NEPTUNE.md) |
| **Status** | ✅ Shipped |
| **Branch** | `feature/graph_evo` |
| **Confidence** | 0.80 — codebase patterns found (extractor → IR → catalog → CLI/MCP; `knowledge/` packs; collectors), no agentspec KB graph domain; novel Neptune facts validated against AWS docs (2026-10-01) |

### Design-time corrections to DEFINE (owner-visible)

| # | DEFINE said | Design does | Evidence |
|---|-------------|-------------|----------|
| C1 | Rule codes `AF-GRAPH-*` | **`AF-GDB-*`** (graph database). `AF-GRAPH-*` already names system-graph refusals (`AF-GRAPH-FORMAT`, `-NOT-FOUND`, `-INVALID`, `-HASH-MISMATCH`, `-KIND`, `-NODE`, `-INPUT`, `-NO-CASE`) | `docs/catalog-contract.md:933-939`, `src/apiforge/graph/export.py:23` |
| C2 | Collector "GET-only" | **Read-only operation allowlist** over `boto3` `neptunedata` (owner approved 2026-10-01). Gremlin/openCypher explain are HTTP POST in Neptune; SPARQL explain has no `neptunedata` operation → dump-only | AWS docs: gremlin-explain-api, access-graph-opencypher-explain, sparql-explain-using |
| C3 | Skill holds `packs/neptune`, `packs/neo4j` | Vendor knowledge as **`knowledge/<domain>/` packs** (existing closed-schema mechanism: `knowledge/neptune` already exists); prose guidance in skill `references/` | `src/apiforge/knowledge/loader.py:1-8` ("A pack is data, not prose"), `knowledge/neptune/pack.yaml` |
| C4 | `AF-DATA-013` extended to Neo4j | Unified fact kind **`data.graph.query`** (measure `vendor`) so the single `AF-DATA-013` check covers both vendors | `src/apiforge/rules/catalog/data.yaml:164-178` (check binds one `kind`) |

A-003 resolved: Gremlin `explain` "doesn't actually run the query"; openCypher `explain=static` "doesn't actually run the query", `dynamic`/`details` run it; SPARQL `static` vs `dynamic`/`details` same split; Gremlin `profile` runs it.

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                         API_GRAPH_NEPTUNE — SYSTEM                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─ OFFLINE CORE (src/apiforge, no network, no provider SDK) ─────────────┐  │
│  │                                                                        │  │
│  │ project tree ─► adapters/graph_/extract.py ──► Fact data.graph.query   │  │
│  │  (.py AST │ .java .go .ts regex+chain join)        │                   │  │
│  │                 │ uses                             ▼                   │  │
│  │      gremlin.py / cypher.py / sparql.py ──► adapters/graph_/ir.py      │  │
│  │      (pure query-text analyzers)            GraphAccessIR v1           │  │
│  │                                              │        │                │  │
│  │                                              │        └► DomainGraph   │  │
│  │                                              │            Sketch (G12) │  │
│  │ plan dump (txt/json) ─► adapters/graph_/plans.py ─► GraphPlanIR v1     │  │
│  │                                              │        │                │  │
│  │                                              ▼        ▼                │  │
│  │                rules/catalog/{data,gdb}.yaml ─► judge ─► findings      │  │
│  │                          AF-DATA-013, AF-GDB-0xx                       │  │
│  │                                                                        │  │
│  │ system graph (nodes/edges.jsonl) ─► graph/export.py                    │  │
│  │                         ├─ jsonl (existing)                            │  │
│  │                         ├─ neptune ─► graph/formats.py OpenCSV         │  │
│  │                         └─ rdf     ─► graph/formats.py N-Triples       │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ COLLECTOR BOUNDARY (src/apiforge/collectors, lazy boto3, receipted) ──┐  │
│  │ collect neptune-explain ─► guards (allowlist, mutation, flag, reader)  │  │
│  │      ─► neptunedata.execute_gremlin_explain_query                      │  │
│  │         neptunedata.execute_open_cypher_explain_query(static)          │  │
│  │         [--profile] execute_gremlin_profile_query / explain dynamic    │  │
│  │      ─► dump dir + CollectManifest ─► consumed by plans.py             │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─ KNOWLEDGE & ROUTING ───────────────────────────────────────────────────┐ │
│  │ agents/api-graph-data-architect.md ─sync─► .claude/.agents/.codex       │ │
│  │ .agents/skills/api-forge-graph/{SKILL.md,references/*} ─sync─► mirrors  │ │
│  │ knowledge/{graph-databases,neptune,neo4j}/ (packs: rules+sources+evals) │ │
│  │ rules/{playbooks,agent_profiles,expertise_triggers}.yaml                │ │
│  │ evals/corpus/{agent-routing,graph-quality}                              │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

Layering (no cycles): `contracts` ← `adapters/graph_` ← `data_governance` / `rules` ← `cli` / `dispatch` / `mcp`. `collectors/graph_explain.py` depends on `collectors/manifest`, `collectors/messaging._boto3/_call` and the pure `adapters/graph_/{gremlin,cypher,sparql}` mutation detectors (pure functions, no I/O) — never the reverse.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `adapters/graph_/gremlin.py` | Parse a Gremlin traversal text into an ordered step list; derive `bounded`, `mutation`, labels, shape risks | stdlib `re`, tokenizer over balanced parens |
| `adapters/graph_/cypher.py` | openCypher analysis: `LIMIT`, variable-length paths, unlabeled nodes, disconnected `MATCH` patterns, mutation clauses, `CALL neptune.algo.*`, vector search | stdlib `re` |
| `adapters/graph_/sparql.py` | SPARQL analysis: `LIMIT`, property paths `+`/`*`, update forms | stdlib `re` |
| `adapters/graph_/extract.py` | Walk the tree; vendor detection (Neptune/Neo4j) per language; Python AST call-chain resolution; Java/Go/TS chain joining; emit `data.graph.query` facts | `ast`, `re` |
| `adapters/graph_/ir.py` | Build `GraphAccessIR` + `DomainGraphSketch` from facts | pydantic contracts |
| `adapters/graph_/plans.py` | Parse plan dumps (7 formats) into `GraphPlanIR`; unknown → `AF-GDB-PLAN-FORMAT` | `re`, `json` |
| `contracts/graph_access.py` | `GraphCallSite`, `GraphAccessIR`, `DomainGraphSketch`, `PlanOperator`, `GraphPlanIR` (all `VersionedContract`) | pydantic v2 |
| `collectors/graph_explain.py` | `collect neptune-explain` with closed allowlist + PROFILE guards + receipt | lazy `boto3` `neptunedata` |
| `graph/formats.py` | OpenCSV and N-Triples writers + offline grammar validators | stdlib `csv` |
| `graph/export.py` | Route `--format jsonl|neptune|rdf` | existing |
| `rules/catalog/gdb.yaml` | Area `GDB` rules `AF-GDB-001..010` (static) and `AF-GDB-020..025` (plan) | YAML closed schema |
| `data_governance.py` | `neptune` + `neo4j` profiles read `shape_risks` from `data.graph.query` | existing |
| `evals/graph_quality.py` | Per-rule × language precision/recall over corpus; exit 1 on threshold breach | existing eval pattern (`evals/cache.py`) |
| `agents/api-graph-data-architect.md` | Owner of graph stores | agent frontmatter contract |
| `.agents/skills/api-forge-graph/` | Procedure + engineering references | SKILL.md + references |
| `knowledge/graph-databases`, `knowledge/neptune` (expanded), `knowledge/neo4j` | Rule ids, sources, matrix, evals per domain | pack closed schema + `scripts/gen_pack_docs.py` |

---

## Key Decisions

### Decision 1: Exclusive graph-store ownership by one vendor-neutral agent

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-01 |

**Context:** Owner wants maximal depth without redundancy. Agent lint enforces one owner per tool (`AF-AGENT-CONTRACT-TOOL-OWNER`, `src/apiforge/dispatch/agent_source.py`) and `agent_audit` flags agents whose `rule_areas` are a subset of another's as merge candidates.

**Choice:** New `api-graph-data-architect` with `rule_areas: [GDB, DATA]` owning `model graph-access`, `model neptune-access`, `model neo4j-access`, `model neptune`, `model graph-explain`, `collect neptune-explain`. `api-data-access-architect` drops `model neptune-access`, `model neptune` and "Neptune" from its description; keeps `[DATA, STORAGE]`.

**Rationale:** `GDB` is unique to the new agent → audit verdict `keep`; neither agent's areas ⊆ the other's (`{GDB,DATA}` vs `{DATA,STORAGE}`); tool ownership stays single. IAM/VPC (infra-reviewer), topology (architecture-reviewer), CloudWatch projection (observability-integration) keep their owners.

**Alternatives Rejected:**
1. `api-neptune-engineer` — duplicates four transversal owners; vendor-per-agent reverses the 52→25 consolidation.
2. Extend data-access — nine stores already; graph modeling/plans/RDF dilute routing.
3. `rule_areas: [GDB, DATA, STORAGE]` — makes data-access `{DATA,STORAGE}` a subset → merge-candidate flag.

**Consequences:**
- Roster 25 → 26; routing corpus gains graph cases; data-access routing cases re-pointed where they mention Neptune.
- Both agents may judge `DATA` rules; only `AF-DATA-013` is graph-specific and its pack is `neptune`/`graph-databases`.

---

### Decision 2: `AF-GDB-*` namespace and `gdb.yaml` area

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-01 |

**Context:** `AF-GRAPH-*` is taken by system-graph refusals (8 codes).
**Choice:** Rules `AF-GDB-NNN` in `src/apiforge/rules/catalog/gdb.yaml` (`area: GDB`); refusals `AF-GDB-<TOPIC>` cataloged in `docs/catalog-contract.md`.
**Rationale:** Avoids semantic collision in catalog lookups, docs and agent reasoning ("graph" = system graph vs graph database).
**Alternatives Rejected:** 1. Reuse `AF-GRAPH-*` with numeric suffix — ambiguous with system-graph refusals. 2. `AF-NEPTUNE-*` — vendor-bound; Neo4j would need a second namespace.
**Consequences:** DEFINE/BRAINSTORM text using `AF-GRAPH-*` for rules is superseded (C1).

---

### Decision 3: Unified fact kind `data.graph.query`

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-01 |

**Context:** Catalog `check` binds one `kind`. DEFINE requires `AF-DATA-013` (ID stable) to cover Neo4j without a second unbounded code.
**Choice:** All graph call sites emit `data.graph.query` with measures `vendor`, `language`, `operation`, `bounded`, `unbounded` (= not bounded, kept for the existing check path), `mutation`, `labels_used`, `edge_labels_used`, `shape_risks`, `binding`, `query_dynamic`. `AF-DATA-013` check → `kind: data.graph.query`, `runtime_scope: "neptune|neo4j"`, title "Graph traversal/query without a limit".
**Rationale:** One rule, one meaning, both vendors; no double report.
**Alternatives Rejected:** 1. Keep `data.neptune.query` + add `AF-DATA-0xx` for Neo4j — duplicate semantics. 2. Allow multi-kind checks — catalog schema change for one rule.
**Consequences:** Update 6 sites (`dbaccess.py` ×3 removed, `data_governance.py:109`, `data.yaml:175`, `knowledge/neptune/evals.yaml:9`, `tests/adapters/test_dbaccess.py:70`). `extract_neptune_access` stays as a thin wrapper (CLI/MCP compatibility).

---

### Decision 4: Collector = closed read-only `neptunedata` allowlist with PROFILE guards

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted (owner, 2026-10-01) |
| **Date** | 2026-10-01 |

**Context:** Plans/cardinality are blind spots. Core must stay offline; collectors already use lazy `boto3` with injected clients (`collectors/datastores.py`). Neptune explain endpoints are POST; SigV4 is handled by boto3.

**Choice:** `collect_neptune_explain(query, language, endpoint, out_dir, *, profile=False, reader_endpoint=None, client=None)`:

| Mode | Operation (allowlist) | Executes query? | Guard |
|------|----------------------|-----------------|-------|
| default gremlin | `execute_gremlin_explain_query` | No | mutation detector |
| default opencypher | `execute_open_cypher_explain_query(explainMode="static")` | No | mutation detector |
| `--profile` gremlin | `execute_gremlin_profile_query` | **Yes** | flag + mutation-free + `--reader-endpoint` == `endpoint` declared reader |
| `--profile` opencypher | `execute_open_cypher_explain_query(explainMode="dynamic")` | **Yes** | same |
| sparql (any) | — | — | refuse `AF-GDB-EXPLAIN-SPARQL`, unlock: import dump via `model graph-explain` |

Any operation name outside the frozenset → `AF-GDB-COLLECT-OP` before the client is touched. Receipt (`CollectManifest.meta`) records `operation`, `executes_query`, `query_sha256`, `endpoint`, `profile`, never credentials.

**Rationale:** Mirrors existing collector boundary; the frozenset is the reviewable safety surface; refusing before any client call makes "no network on refusal" testable with an injected client that raises if touched.

**Alternatives Rejected:**
1. Literal GET-only HTTP with manual SigV4 — Gremlin/openCypher explain are POST; manual signing adds untested crypto code.
2. Unrestricted PROFILE — executes arbitrary reads on writer instances.
3. No collector — owner asked for optional collector.

**Consequences:**
- `--reader-endpoint` is a declaration, not proof the endpoint is a reader (receipt says `reader_declared`, not `reader_verified`).
- Mutation detection is lexical; dynamic query text (`query_dynamic`) is refused for `--profile` (`AF-GDB-PROFILE-DYNAMIC`).

---

### Decision 5: Knowledge in `knowledge/` packs, prose in skill references

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-01 |

**Context:** `knowledge/<domain>/` packs exist with a closed schema, generated docs and selector triggers; `knowledge/neptune` is thin (2 rules, 2 evals). Packs forbid authored prose.
**Choice:** New pack `graph-databases` (areas `[GDB, DATA]`, vendor-neutral rules, sources TinkerPop/openCypher/W3C), expand `neptune` (AWS sources: explain/profile, bulk loader, Streams, Analytics, IAM; Analytics rules; matrix engine 1.2–1.4), new `neo4j` (vendor-docs sources, Neo4j plan rule). Engineering prose (modeling, traversal design, plan reading, Neptune/Neo4j operations) lives in `.agents/skills/api-forge-graph/references/`. `expertise_triggers.yaml`: `graph-databases` triggers on gremlin/opencypher/cypher/sparql/traversal/property graph/rdf; `neptune` → `[neptune, graph-databases]`; `neo4j` → `[neo4j, graph-databases]`.
**Rationale:** Reuses the selector and `knowledge check`; avoids a second "pack" concept; respects the data-not-prose contract.
**Alternatives Rejected:** Skill `packs/` folders — a parallel, unchecked pack mechanism.
**Consequences:** Pack docs regenerate with `scripts/gen_pack_docs.py`; Neptune numeric cost stays out (qualitative note in `references/neptune.md`).

---

### Decision 6: Multi-line chains — AST expression in Python, chain joining elsewhere

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-01 |

**Context:** Today a chain split across lines is conservatively `unbounded` (`dbaccess.py:310-311`).
**Choice:** Python: take the **outermost** `ast.Call` whose attribute chain roots at `<name>.V(`/`.E(` (or `g.with*(...)`), render it with `ast.get_source_segment`, analyze full text once (inner calls of the same chain are skipped by node identity). Java/Go/TS: join a line with following lines that start (after whitespace) with `.` until the statement ends (`;` for Java/TS, unbalanced-paren close or non-`.` line for Go), then analyze; report the start line.
**Rationale:** One fact per traversal, real bounds detection, still no execution.
**Alternatives Rejected:** tree-sitter grammars for Java/Go/TS — new dependency; owner accepted regex heuristics with declared diagnostics.
**Consequences:** Regex languages keep `AF-GDB-HEURISTIC` diagnostic per file; precision threshold for them is ≥ 0.90, not 1.00.

---

### Decision 7: Export formats deterministic, all-String OpenCSV and IRI-namespaced N-Triples

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-01 |

**Choice:** `neptune` → `vertices.csv` (`~id,~label,<prop>:String…` union header, sorted columns, empty cell = absent) and `edges.csv` (`~id,~from,~to,~label,<prop>:String…`), edge `~id = stable_id(from,to,kind)`; nested values JSON-serialized. `rdf` → `graph.nt`: `<urn:apiforge:node:ID> <rdf:type> <urn:apiforge:kind:KIND>`, edges `<urn:apiforge:node:FROM> <urn:apiforge:edge:KIND> <urn:apiforge:node:TO>`, props `"<value>"` literals under `<urn:apiforge:prop:KEY>`, IRIs percent-encoded, literals N-Triples-escaped; lines sorted. `export.json` keeps digests of every written file; `GraphExport.format` adds `"rdf"`.
**Rationale:** Byte-deterministic output (existing export contract); all-String avoids guessing types (no inference rule).
**Alternatives Rejected:** typed columns inferred from values — inference violates "declared, never inferred".
**Consequences:** Numeric querying in Neptune needs a cast; documented in `references/system-graph-bridge.md`.

---

## File Manifest

Agents: agentspec specialists discovered under the plugin (`python-developer`, `test-generator`, `code-documenter`, `aws-data-architect`) — project agents are routing targets, not builders.

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| **W1 — knowledge & routing** |
| 1 | `agents/api-graph-data-architect.md` | Create | New owner agent (English, sections per contract) | @code-documenter | None |
| 2 | `agents/api-data-access-architect.md` | Modify | Drop Neptune tools/description; route graph → 1 | @code-documenter | 1 |
| 3 | `.claude/agents/*`, `.agents/agents/*`, `.codex/agents/*` | Generate | `apiforge agents sync` | (general) | 1, 2 |
| 4 | `src/apiforge/rules/playbooks.yaml` | Modify | Playbook for 1; remove neptune purpose text from data-access | (general) | 1 |
| 5 | `src/apiforge/rules/agent_profiles.yaml` | Modify | Profile `api-graph-review` (unique capability) | (general) | 1 |
| 6 | `src/apiforge/rules/expertise_triggers.yaml` | Modify | `graph-databases`, `neptune`, `neo4j` triggers | (general) | 19-21 |
| 7 | `.agents/skills/api-forge-graph/SKILL.md` | Create | Procedure, commands, refusals (pt-BR like siblings) | @code-documenter | 1 |
| 8 | `.agents/skills/api-forge-graph/references/modeling.md` | Create | Property graph vs RDF, supernodes, edge vs property, cardinality | @code-documenter | 7 |
| 9 | `.agents/skills/api-forge-graph/references/gremlin.md` | Create | Traversal patterns/anti-patterns ↔ AF-GDB rules | @code-documenter | 7 |
| 10 | `.agents/skills/api-forge-graph/references/opencypher.md` | Create | Cypher patterns, var-length paths, Neptune vs Neo4j dialect | @code-documenter | 7 |
| 11 | `.agents/skills/api-forge-graph/references/sparql.md` | Create | Property paths, LIMIT, update forms | @code-documenter | 7 |
| 12 | `.agents/skills/api-forge-graph/references/plans.md` | Create | Reading explain/profile per format; AF-GDB-02x | @code-documenter | 7 |
| 13 | `.agents/skills/api-forge-graph/references/performance.md` | Create | Fan-out, path explosion, pagination, supernode handling | @code-documenter | 7 |
| 14 | `.agents/skills/api-forge-graph/references/neptune.md` | Create | Database vs Analytics, loader, Streams, IAM/SigV4, network, snapshots, CloudWatch, qualitative cost | @aws-data-architect | 7 |
| 15 | `.agents/skills/api-forge-graph/references/neo4j.md` | Create | Driver, dialect, indexes/constraints, plans | @code-documenter | 7 |
| 16 | `.agents/skills/api-forge-graph/references/system-graph-bridge.md` | Create | Export usage, domain sketch, casting | @code-documenter | 7 |
| 17 | `.agents/skills/api-forge-data-access/SKILL.md` | Modify | Remove Neptune ownership; point to api-forge-graph | @code-documenter | 7 |
| 18 | `.claude/skills/api-forge-graph/**`, other mirrors | Generate | `python scripts/sync_skills.py` | (general) | 7-17 |
| 19 | `knowledge/graph-databases/{pack.yaml,source_authority.yaml,evals.yaml,matrix.yaml}` + generated docs | Create | Vendor-neutral pack | @code-documenter | 22 |
| 20 | `knowledge/neptune/{pack.yaml,source_authority.yaml,evals.yaml,matrix.yaml}` + generated docs | Modify | Expand Neptune pack | @aws-data-architect | 22 |
| 21 | `knowledge/neo4j/{pack.yaml,source_authority.yaml,evals.yaml,matrix.yaml}` + generated docs | Create | Neo4j pack | @code-documenter | 22 |
| 22 | `src/apiforge/rules/catalog/gdb.yaml` | Create | `AF-GDB-001..010`, `020..025` | @python-developer | None |
| 23 | `src/apiforge/rules/catalog/data.yaml` | Modify | `AF-DATA-013` → `data.graph.query`, scope `neptune|neo4j` | @python-developer | 22 |
| 24 | `evals/corpus/agent-routing/cases.json` | Modify | ≥ 6 graph cases (Gremlin, Cypher, SPARQL, Neo4j, plan, export); re-point Neptune cases | @test-generator | 1 |
| 25 | `CLAUDE.md`, `AGENTS.md` | Modify | Routing line: graph stores → `api-forge-graph` | (general) | 7 |
| **W2 — GraphAccessIR + static rules** |
| 26 | `src/apiforge/contracts/graph_access.py` | Create | `GraphCallSite`, `GraphAccessIR`, `DomainGraphSketch`, `PlanOperator`, `GraphPlanIR` | @python-developer | None |
| 27 | `src/apiforge/adapters/graph_/__init__.py` | Create | Package exports | @python-developer | 28-31 |
| 28 | `src/apiforge/adapters/graph_/gremlin.py` | Create | Step parser + bounded/mutation/labels/risks | @python-developer | None |
| 29 | `src/apiforge/adapters/graph_/cypher.py` | Create | openCypher analyzer (+ Analytics `CALL neptune.algo.*`, vector topK) | @python-developer | None |
| 30 | `src/apiforge/adapters/graph_/sparql.py` | Create | SPARQL analyzer | @python-developer | None |
| 31 | `src/apiforge/adapters/graph_/extract.py` | Create | Tree walk, vendor detection, Py AST, Java/Go/TS chain join | @python-developer | 28-30 |
| 32 | `src/apiforge/adapters/graph_/ir.py` | Create | Facts → `GraphAccessIR` + `DomainGraphSketch` | @python-developer | 26, 31 |
| 33 | `src/apiforge/adapters/dbaccess.py` | Modify | Remove Neptune scanners; `extract_neptune_access` delegates to 31 | @python-developer | 31 |
| 34 | `src/apiforge/data_governance.py` | Modify | `neo4j` support; risks from `shape_risks`; mutation set incl. Cypher/SPARQL verbs | @python-developer | 31 |
| 35 | `src/apiforge/contracts/stubs.py` | Modify | Allow `neo4j` in `DataAccessReadiness`/`DataPerformanceProfile` database literal | @python-developer | 34 |
| 36 | `src/apiforge/cli.py` | Modify | `model graph-access`, `model neo4j-access` (+ keep `neptune-access`); `model graph-explain`; `collect neptune-explain`; `graph export --format neptune|rdf`; `evals graph-quality` | @python-developer | 31, 37, 41, 44, 47 |
| 37 | `src/apiforge/dispatch/runner.py`, `src/apiforge/mcp/tools.py` | Modify | Same verbs over MCP with refusal `field`/`unlock` | @python-developer | 36 |
| 38 | `evals/corpus/graph-quality/cases.json` + `fixtures/{py,java,go,ts}/…` | Create | Golden corpus (≥2 pos + ≥1 neg per rule × language) | @test-generator | 22, 31 |
| 39 | `src/apiforge/evals/graph_quality.py` | Create | Scorer + thresholds | @python-developer | 38 |
| 40 | `tests/adapters/test_graph_extract.py`, `tests/adapters/test_graph_analyzers.py`, `tests/adapters/test_dbaccess.py` (modify) | Create/Modify | Unit tests AT-002..007 | @test-generator | 28-34 |
| **W3 — plans** |
| 41 | `src/apiforge/adapters/graph_/plans.py` | Create | 7 plan parsers → `GraphPlanIR`; plan rule measures | @python-developer | 26 |
| 42 | `tests/fixtures/graph_explain/{gremlin-explain,gremlin-profile,cypher-static,cypher-dynamic,sparql-explain,neo4j-explain,neo4j-profile}.*` + `SYNTHETIC.md` | Create | Synthetic fixtures (official-doc shapes), labeled | @test-generator | None |
| 43 | `tests/adapters/test_graph_plans.py` | Create | AT-008, AT-009, AF-GDB-02x | @test-generator | 41, 42 |
| **W4 — collector** |
| 44 | `src/apiforge/collectors/graph_explain.py` | Create | Allowlisted collector + guards + receipt | @aws-data-architect | 28-30 |
| 45 | `tests/collectors/test_graph_explain.py` | Create | AT-010..012 + allowlist + no-call-on-refusal | @test-generator | 44 |
| **W5 — export + Analytics** |
| 46 | `src/apiforge/graph/formats.py` | Create | OpenCSV/N-Triples writers + validators | @python-developer | None |
| 47 | `src/apiforge/graph/export.py`, `src/apiforge/contracts/graph.py` | Modify | Route formats; `format` literal adds `rdf` | @python-developer | 46 |
| 48 | `tests/graph/test_graph_export_formats.py` | Create | AT-013, AT-014 round-trip | @test-generator | 47 |
| 49 | `tests/adapters/test_graph_analytics.py` | Create | AT-015 (Analytics, vector) | @test-generator | 29 |
| **Docs & SDD (all waves)** |
| 50 | `docs/contracts/GraphAccess-v1.md`, `docs/contracts/GraphPlan-v1.md` | Create | Contract docs | @code-documenter | 26 |
| 51 | `docs/catalog-contract.md` | Modify | Catalog `AF-GDB-*` refusal codes + heuristic codes | @code-documenter | 22, 41, 44 |
| 52 | `README.md` | Modify | New commands | @code-documenter | 36 |
| 53 | `docs/sdd/API_GRAPH_NEPTUNE/{discover,intent,contract,architecture,plan,build,verify,secure,benchmark,ship}.md` + `evidence/` | Create | Repo SDD chain for `apiforge sdd check` | @code-documenter | all |
| 54 | `tests/knowledge/test_packs.py` (modify), `tests/dispatch|agentops` routing tests (modify as needed) | Modify | Pack + routing assertions | @test-generator | 19-21, 24 |
| **W6 — field + gates** |
| 55 | `docs/field/` ledger entry | Create | Field cycle (`unresolved` until target repo) | (general) | all |

**Total Files:** 55 manifest rows (≈ 75 physical files incl. fixtures, generated pack docs and mirrors).

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @python-developer | 22, 23, 26-37, 39, 41, 46, 47 | Typed pydantic contracts, AST/regex parsers, dataclass-free pure functions matching repo style |
| @test-generator | 24, 38, 40, 42, 43, 45, 48, 49, 54 | pytest fixtures, golden corpus construction, refusal tests |
| @code-documenter | 1, 2, 7-13, 15-17, 19, 21, 50-53 | Agent/skill/reference/contract prose |
| @aws-data-architect | 14, 20, 44 | Neptune operations, neptunedata API, IAM/SigV4 boundary |
| (general) | 3, 4, 5, 6, 18, 25, 55 | Generated mirrors and small YAML registry edits |

**Agent Discovery:** scanned `C:/Users/edgar/.claude/plugins/cache/agentspec/agentspec/3.5.0/agents/**`; matched by file type (.py → python-developer, tests → test-generator, .md → code-documenter) and keywords (Neptune/boto3 → aws-data-architect).

---

## Code Patterns

### Pattern 1: Contracts (`src/apiforge/contracts/graph_access.py`)

```python
"""GraphAccessIR / GraphPlanIR v1 — typed graph-database evidence."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from apiforge.contracts.base import VersionedContract

Vendor = Literal["neptune", "neo4j"]
Language = Literal["gremlin", "opencypher", "sparql"]
ShapeRisk = Literal[
    "repeat-without-stop",
    "fanout-without-edge-label",
    "unfiltered-start",
    "open-variable-length-path",
    "unlabeled-node-pattern",
    "cartesian-pattern",
    "unbounded-property-path",
    "dynamic-query-text",
    "analytics-unscoped-algorithm",
    "vector-search-without-topk",
]


class GraphCallSite(VersionedContract):
    fact_id: str
    vendor: Vendor
    language: Language
    operation: str
    path: str
    line: int
    sha256: str
    query_text: str | None = None
    query_dynamic: bool = False
    bounded: bool
    mutation: bool
    labels_used: tuple[str, ...] = ()
    edge_labels_used: tuple[str, ...] = ()
    shape_risks: tuple[ShapeRisk, ...] = ()


class DomainGraphSketch(VersionedContract):
    vertex_labels: tuple[str, ...] = ()
    edge_labels: tuple[str, ...] = ()
    edges: tuple[tuple[str | None, str, str | None], ...] = ()
    evidence: tuple[str, ...] = ()


class GraphAccessIR(VersionedContract):
    id: str
    root: str
    call_sites: tuple[GraphCallSite, ...] = ()
    sketch: DomainGraphSketch = Field(default_factory=DomainGraphSketch)
    unresolved: tuple[str, ...] = ()


PlanFormat = Literal[
    "neptune-gremlin-explain",
    "neptune-gremlin-profile",
    "neptune-opencypher-static",
    "neptune-opencypher-dynamic",
    "neptune-sparql-explain",
    "neo4j-explain",
    "neo4j-profile",
]


class PlanOperator(VersionedContract):
    op_id: str
    name: str
    arguments: str = ""
    units_in: int | None = None
    units_out: int | None = None
    estimate: str | None = None
    native: bool = True


class GraphPlanIR(VersionedContract):
    id: str
    format: PlanFormat
    executed: bool
    source_sha256: str
    synthetic: bool = False
    operators: tuple[PlanOperator, ...] = ()
    warnings: tuple[str, ...] = ()
    predicate_count: int | None = None
```

### Pattern 2: Gremlin step parsing (`adapters/graph_/gremlin.py`)

```python
"""Gremlin traversal text → ordered steps; no execution, no inference."""

from __future__ import annotations

import re
from dataclasses import dataclass

_STEP = re.compile(r"\.\s*([A-Za-z_]\w*)\s*\(")
_MUTATING = frozenset({"addV", "addE", "drop", "property", "mergeV", "mergeE"})
_FANOUT = frozenset({"out", "in", "both", "outE", "inE", "bothE"})
_BOUNDS = frozenset({"limit", "range", "tail", "next", "count"})


@dataclass(frozen=True)
class Step:
    name: str
    args: str


def _args_at(text: str, start: int) -> str:
    depth, i = 1, start
    while i < len(text) and depth:
        depth += {"(": 1, ")": -1}.get(text[i], 0)
        i += 1
    return text[start : i - 1]


def steps(traversal: str) -> tuple[Step, ...]:
    return tuple(Step(m.group(1), _args_at(traversal, m.end())) for m in _STEP.finditer(traversal))


def analyze(traversal: str) -> dict[str, object]:
    chain = steps(traversal)
    names = [s.name for s in chain]
    risks: list[str] = []
    for index, step in enumerate(chain):
        if step.name == "repeat" and not {"times", "until"} & set(names[index + 1 :]):
            risks.append("repeat-without-stop")
        if step.name in _FANOUT and not step.args.strip():
            risks.append("fanout-without-edge-label")
    if names[:1] in (["V"], ["E"]) and not chain[0].args.strip() and not {
        "hasLabel", "has", "hasId"
    } & set(names[1:2]):
        risks.append("unfiltered-start")
    return {
        "bounded": bool(_BOUNDS & set(names)),
        "mutation": bool(_MUTATING & set(names)),
        "labels_used": tuple(sorted({a.strip("'\" ") for s in chain if s.name == "hasLabel" for a in s.args.split(",")})),
        "edge_labels_used": tuple(sorted({a.strip("'\" ") for s in chain if s.name in _FANOUT and s.args.strip() for a in s.args.split(",")})),
        "shape_risks": tuple(dict.fromkeys(risks)),
    }
```

### Pattern 3: Python chain resolution (`adapters/graph_/extract.py`)

```python
def _outermost_traversals(tree: ast.Module) -> list[ast.Call]:
    """Outermost call whose attribute chain roots at <name>.V(...)/.E(...)."""
    inner: set[int] = set()
    found: list[ast.Call] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or id(node) in inner:
            continue
        cursor: ast.AST = node
        chain: list[ast.Call] = []
        while isinstance(cursor, ast.Call) and isinstance(cursor.func, ast.Attribute):
            chain.append(cursor)
            cursor = cursor.func.value
        root = chain[-1] if chain else None
        if root is not None and root.func.attr in ("V", "E") and isinstance(cursor, ast.Name):
            found.append(node)
            inner.update(id(c) for c in chain[1:])
    return found
```

`ast.walk` is breadth-first from the module, so the outermost call of a chain is visited before its inner calls; the `inner` set prevents duplicate facts.

### Pattern 4: Collector guards (`collectors/graph_explain.py`)

```python
_ALLOWED = frozenset(
    {
        "execute_gremlin_explain_query",
        "execute_gremlin_profile_query",
        "execute_open_cypher_explain_query",
    }
)


def _refuse(code: str, detail: str, field: str, unlock: str) -> CollectError:
    error = CollectError(code, detail)
    error.field, error.unlock = field, unlock
    return error


def _plan(language: str, query: str, *, profile: bool, endpoint: str, reader: str | None) -> tuple[str, dict[str, str]]:
    if language == "sparql":
        raise _refuse("AF-GDB-EXPLAIN-SPARQL", "neptunedata has no SPARQL explain operation",
                      "language", "run explain=static yourself and import it with `model graph-explain`")
    analysis = analyze_query(language, query)  # pure, from adapters/graph_
    if analysis["mutation"]:
        raise _refuse("AF-GDB-PROFILE-MUTATION", "query mutates the graph", "query",
                      "submit a read-only query; API Forge never explains mutations")
    if not profile:
        if language == "gremlin":
            return "execute_gremlin_explain_query", {"gremlinQuery": query}
        return "execute_open_cypher_explain_query", {"openCypherQuery": query, "explainMode": "static"}
    if reader is None or reader != endpoint:
        raise _refuse("AF-GDB-PROFILE-READER", "PROFILE executes the query", "reader_endpoint",
                      "pass --reader-endpoint equal to --endpoint, naming a reader instance")
    if language == "gremlin":
        return "execute_gremlin_profile_query", {"gremlinQuery": query}
    return "execute_open_cypher_explain_query", {"openCypherQuery": query, "explainMode": "dynamic"}
```

`collect_neptune_explain` calls `_plan` **before** creating or touching the client; asserts `operation in _ALLOWED`; writes the response with `write_artifact`; records `executes_query` in the manifest. `--profile` absent + request for an executing mode is unrepresentable (the only switch is `profile`). Dynamic text (`query_dynamic`) with `--profile` → `AF-GDB-PROFILE-DYNAMIC`.

### Pattern 5: Catalog rule (`rules/catalog/gdb.yaml`)

```yaml
catalog_version: 1
schema_version: 1
area: GDB
retrieved: "2026-10-01"
rules:
  - id: AF-GDB-001
    title: "Gremlin repeat() without times() or until()"
    severity: high
    rationale: >
      A repeat() step with no declared stop expands until the frontier is
      exhausted; on a connected graph the path count grows combinatorially.
    remediation: "Bound the loop with .times(n) or .until(<predicate>) and keep a .limit()."
    reference: "https://tinkerpop.apache.org/docs/current/reference/#repeat-step"
    runtime_scope: "neptune|neo4j"
    check:
      kind: data.graph.query
      path: measures.repeat_without_stop
      op: eq
      value: true
```

Each shape risk is also emitted as a boolean measure (`repeat_without_stop`, `fanout_without_edge_label`, …) so every rule is a plain `eq true` check — no catalog schema change.

### Pattern 6: Agent frontmatter (`agents/api-graph-data-architect.md`)

```yaml
---
name: api-graph-data-architect
description: >-
  Use when the question is a graph database: property graph or RDF modeling, Gremlin, openCypher or
  SPARQL traversals, explain/profile plans, supernodes, Neptune Database/Analytics or Neo4j posture,
  and exporting the system graph to a graph store. Not for relational or document stores (-> api-data-access-architect).
access: read-only
model_tier: deep
rule_areas: [GDB, DATA]
executors: [af-inventory, af-extractor, af-judge, af-verifier, af-synthesizer]
apiforge_tools: [model graph-access, model neptune-access, model neo4j-access, model neptune, model graph-explain, collect neptune-explain, graph export]
---
```

Body sections must match `REQUIRED_SECTIONS` and the word band checked by `lint_agent`; language English (`AF-AGENT-CONTRACT-LANGUAGE`). `graph export` ownership must be checked against the current owner during build — if owned, omit it from this list and reference it in the body only.

### Pattern 7: Eval command (`cli.py`, mirrors `evals cache`)

```python
@evals_app.command("graph-quality")
def evals_graph_quality(
    corpus: Path = typer.Option(Path("evals/corpus/graph-quality"), "--corpus"),
    detail_level: str = typer.Option("normal", "--detail-level", help=_DETAIL_HELP),
) -> None:
    """Per-rule x language precision/recall over the graph golden corpus."""
    from apiforge.evals.graph_quality import run_graph_quality

    result = _run(lambda: run_graph_quality(corpus))
    _echo_json(result, detail_level)
    if isinstance(result, dict) and not result.get("passed"):
        raise typer.Exit(code=1)
```

### Pattern 8: Thresholds (configuration as data)

```yaml
# evals/corpus/graph-quality/thresholds.yaml
precision:
  python: 1.00
  java: 0.90
  go: 0.90
  typescript: 0.90
recall_global: 0.90
bounded_false_positives: 0
min_cases_per_rule_language: {positive: 2, negative: 1}
```

---

## Data Flow

```text
1. Operator runs `apiforge model graph-access --path <repo>`
   │
   ▼
2. extract.py walks files; per language detects vendor (imports: gremlin_python,
   gremlingo, gremlin (npm), org.apache.tinkerpop, neo4j drivers, boto3 neptunedata)
   │
   ▼
3. Query text → gremlin/cypher/sparql analyzer → measures → Fact data.graph.query
   │
   ▼
4. ir.py → GraphAccessIR (+ DomainGraphSketch from labels/edge labels)
   │
   ▼
5. judge applies AF-DATA-013 + AF-GDB-001..010 → findings citing fact_id
   │
   ├─► (optional) `collect neptune-explain` → dump + receipt
   │                │
   ▼                ▼
6. `model graph-explain --path <dump>` → GraphPlanIR → AF-GDB-020..025
   │
   ▼
7. Agent answers; any question without a plan → `unresolved`
   │
   ▼
8. `graph export --format neptune|rdf` → OpenCSV / N-Triples + export.json digests
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| Amazon Neptune data API | `boto3` `neptunedata` (collector only, lazy import, injected client in tests) | SigV4 via boto3 default credential chain; never stored |
| Neptune cluster API | existing `collect neptune` (`rds:DescribeDBClusters`) | unchanged |
| Neo4j | none (dumps only) | — |
| Neptune bulk loader / RDF consumers | files produced by export | — |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit — analyzers | Gremlin/Cypher/SPARQL pure functions | `tests/adapters/test_graph_analyzers.py` | pytest, parametrize | every shape risk + negative |
| Unit — extraction | Py AST, Java/Go/TS chain join, vendor detection | `tests/adapters/test_graph_extract.py`, `test_dbaccess.py` | pytest + fixtures | AT-002..007 |
| Unit — plans | 7 formats + unknown + missing | `tests/adapters/test_graph_plans.py` | pytest | AT-008, AT-009 |
| Unit — collector | allowlist, guards, receipt, no-client-call on refusal | `tests/collectors/test_graph_explain.py` | pytest + fake client raising on any attribute | AT-010..012 |
| Unit — export | OpenCSV/N-Triples writers + validators, counts, determinism | `tests/graph/test_graph_export_formats.py` | pytest | AT-013, AT-014 |
| Unit — Analytics | `CALL neptune.algo.*`, vector topK | `tests/adapters/test_graph_analytics.py` | pytest | AT-015 |
| Golden eval | corpus precision/recall | `apiforge evals graph-quality` | CLI | AT-016 + thresholds |
| Contract | catalog load, pack check, agent lint, skills validate | `tests/knowledge/test_packs.py`, `apiforge agents lint`, `scripts/validate_skills.py`, `apiforge knowledge check` | CLI + pytest | 0 errors |
| Routing | graph questions → new agent | `evals/corpus/agent-routing/cases.json` via agent-routing eval | CLI | AT-001; no regression vs baseline |
| CLI/MCP parity | refusals carry `code`,`field`,`unlock` | `tests/mcp/…`, `tests/dispatch/…` | pytest | every new refusal |
| Gates | economy-hardening, agentic-quality baseline, sdd check | CLI | — | pass |
| Full suite | once before ship | `pytest --basetemp E:/afpt` | pytest | green |

Acceptance mapping: AT-001 routing; AT-002/003/004/005/006/007 extraction+analyzers; AT-008/009 plans; AT-010/011/012 collector; AT-013/014 export; AT-015 analytics; AT-016 eval gate.

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| `.py` parse failure | Diagnostic `AF-GDB-PARSE` (file, line), scan continues | No |
| Regex-language heuristic | Diagnostic `AF-GDB-HEURISTIC` per file | No |
| Dynamic query text (f-string/concat/variable) | `query_dynamic=true`, `bounded` unknown → measure `unbounded` stays true only if no bound step visible; IR `unresolved` entry | No |
| Unknown plan format | `AF-GDB-PLAN-FORMAT` (field `path`, unlock: name `--format`) | No |
| Plan parse failure | `AF-GDB-PLAN-PARSE` with line | No |
| Collector op outside allowlist | `AF-GDB-COLLECT-OP` before client creation | No |
| SPARQL explain via collector | `AF-GDB-EXPLAIN-SPARQL` | No |
| PROFILE mutation / missing reader / dynamic text | `AF-GDB-PROFILE-MUTATION` / `-READER` / `-DYNAMIC` | No |
| AWS call failure | existing `AF-COLLECT-AWS` | No (operator re-runs) |
| boto3 absent | existing `AF-COLLECT-AWS` install hint | No |
| Export unknown format | existing `AF-GRAPH-FORMAT` | No |
| Export missing graph | existing `AF-GRAPH-NOT-FOUND` | No |
| Eval threshold breach | exit 1, failing rule × language named | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `evals/corpus/graph-quality/thresholds.yaml` | YAML | per Pattern 8 | Precision/recall gates |
| `collect neptune-explain --endpoint` | string | required | Neptune cluster/instance endpoint URL |
| `--language` | enum | required | `gremlin|opencypher|sparql` |
| `--profile` | bool | `false` | Allow executing plans (guarded) |
| `--reader-endpoint` | string | none | Declared reader; must equal `--endpoint` for `--profile` |
| `model graph-explain --format` | enum | auto-detect by header | One of 7 `PlanFormat` values |
| `model graph-explain --synthetic` | bool | `false` | Marks plan IR as synthetic evidence |
| `graph export --format` | enum | `jsonl` | `jsonl|neptune|rdf` |

---

## Security Considerations

- PROFILE/dynamic explain execute queries: triple guard (flag, mutation-free static text, declared reader); refusal happens before any client exists.
- Allowlist is a frozenset reviewed in tests; adding an operation requires a test change.
- Receipts store `query_sha256`, not credentials; query text in dumps may contain literals → `references/neptune.md` instructs redaction before committing real samples (A-002).
- `AF-GDB-008` (dynamic query text) highlights Gremlin/Cypher injection risk; security exploitation analysis stays with `api-security-reviewer`.
- Core never imports `boto3`; collector uses existing lazy `_boto3` helper.
- Synthetic fixtures flagged (`synthetic: true` in `GraphPlanIR`, `SYNTHETIC.md` in fixture dir) and never counted as field evidence.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Existing CLI JSON envelope (`_echo_json`), diagnostics list per run |
| Metrics | `evals graph-quality` report: per rule × language TP/FP/FN, precision, recall |
| Tracing | Provenance: `fact_id` → `SourceRef(path, sha256, line)`; plan → dump sha256; collector → manifest digests |

---

## Pipeline Architecture (if applicable)

Not a data pipeline: inputs are source trees, dumps and graph files processed on demand. Data contract handled by `GraphAccessIR`/`GraphPlanIR` versioned schemas (v2 lands as sibling class per `VersionedContract`).

### Data Quality Gates

| Gate | Tool | Threshold | Action on Failure |
|------|------|-----------|-------------------|
| Facts carry provenance | unit tests | 100% `SourceRef` | Block build |
| Plan fixtures parse | `test_graph_plans.py` | 100% | Block build |
| Corpus precision/recall | `evals graph-quality` | Pattern 8 | Exit 1 |
| Export grammar | validators in `formats.py` | 0 invalid lines | Block |

---

## Wave Plan & Verification Gates

| Wave | Manifest rows | Targeted verification |
|------|---------------|-----------------------|
| W1 | 1-25 | `apiforge agents sync && apiforge agents lint`; `python scripts/sync_skills.py && python scripts/validate_skills.py`; `apiforge knowledge check`; `python scripts/gen_pack_docs.py`; agent-routing eval vs baseline |
| W2 | 26-40 | `pytest tests/adapters -k "graph or dbaccess" --basetemp E:/afpt`; `apiforge evals graph-quality` |
| W3 | 41-43 | `pytest tests/adapters/test_graph_plans.py --basetemp E:/afpt` |
| W4 | 44-45 | `pytest tests/collectors/test_graph_explain.py --basetemp E:/afpt` |
| W5 | 46-49 | `pytest tests/graph tests/adapters/test_graph_analytics.py --basetemp E:/afpt` |
| W6 | 50-55 | `apiforge evals economy-hardening`; `apiforge evals agentic-quality --baseline <prev>`; `apiforge sdd check --root docs/sdd`; full `pytest --basetemp E:/afpt`; field ledger |

Unresolved carried to ship: real redacted samples (A-002), field target repo, regex-language heuristics, `--reader-endpoint` declared not verified, DomainGraphSketch ↔ system-graph link limited to evidence paths (no new `EdgeKind`).

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-10-01 | design-agent | Initial version; corrections C1-C4 (AF-GDB namespace, allowlist collector, knowledge packs, unified fact kind) |
| 1.1 | 2026-10-01 | ship-agent | Shipped and archived (commit 698b46b) |

---

## Next Step

**Ready for:** `/agentspec:workflow:ship .claude/sdd/features/DEFINE_API_GRAPH_NEPTUNE.md`
