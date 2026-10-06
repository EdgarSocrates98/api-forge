# DEFINE: API Graph & Neptune Specialization

> A vendor-neutral graph-database specialist for API Forge — one agent, one skill with Neptune and Neo4j packs, typed graph evidence, plan reading, a guarded explain collector and system-graph export — without redundant ownership.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_GRAPH_NEPTUNE |
| **Date** | 2026-10-01 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 14/15 |
| **Upstream** | `.claude/sdd/features/BRAINSTORM_API_GRAPH_NEPTUNE.md` (Approach A) |
| **Branch** | `feature/graph_evo` |

---

## Problem Statement

API Forge detects that code calls Neptune but cannot model, query-engineer, plan-read or export graph data with specialist depth: query plans and cardinality are declared blind spots (`agents/api-data-access-architect.md:15`), the only graph rule is a same-line `unbounded` heuristic (`AF-DATA-013`), the `--format neptune` export is a stub (`src/apiforge/graph/export.py:18`), and graph-store questions have no dedicated owner — so unbounded traversals, supernodes and path explosion surface only in production.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| API engineer on a graph-backed service | Writes Gremlin/openCypher/SPARQL against Neptune or Neo4j | Multi-line unbounded chains, `repeat()` without a stop, open variable-length paths and full-graph algorithms pass review undetected |
| API Forge host agent (Claude/Codex/Devin via CLI/MCP) | Routes a graph question to a specialist | No owner for graph modeling or plan questions; `api-data-access-architect` declares them blind spots |
| Platform/data architect | Reads plans and cluster posture | Must read Neptune explain/profile by hand; no typed plan evidence or rules |
| Architect using the Forge system graph | Wants the workspace graph in a graph DB | `graph export --format neptune` is a stub; no RDF output |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | G1 — Agent `api-graph-data-architect` (vendor-neutral) owns graph stores; `api-data-access-architect` cedes `model neptune-access` and `model neptune` and routes graph stores to it |
| **MUST** | G2 — Skill `api-forge-graph` with `references/` (modeling, gremlin, opencypher, sparql, performance, system-graph-bridge) and `packs/neptune`, `packs/neo4j` |
| **MUST** | G3 — `GraphAccessIR` contract: per call site `vendor`, `language`, `query_text?`, `labels_used`, `edge_labels_used`, `bounded`, `mutation`, `shape_risks[]`, `evidence_ref` |
| **MUST** | G4 — Extraction for Neptune + Neo4j: Python AST; Java/Go/TypeScript declared regex heuristics (TS is new); multi-line Gremlin chains resolved |
| **MUST** | G5 — Rule area `graph` (`src/apiforge/rules/catalog/graph.yaml`) with `AF-GRAPH-*` rules for risks not already covered; `AF-DATA-013` keeps its ID as the single unbounded-result rule (extended to Neo4j) — no double-reporting |
| **MUST** | G6 — Golden corpus + `apiforge evals graph-quality` with thresholds in Success Criteria |
| **MUST** | G7 — `GraphPlanIR` + `model graph-explain` parsing Neptune Gremlin explain/profile, openCypher explain (static/dynamic), SPARQL explain, Neo4j EXPLAIN/PROFILE dumps; plan rules over expensive operators |
| **MUST** | G8 — `collect neptune-explain`: outside core, GET-only, receipted; default non-executing explain; executing PROFILE only behind guards |
| **MUST** | G9 — `graph export --format neptune` (bulk-loader OpenCSV vertices/edges) and `--format rdf` (N-Triples), round-trip validated |
| **MUST** | G10 — Routing/IR/host mirrors updated (`CLAUDE.md`, `AGENTS.md`, agent routing IR, `apiforge agents sync`) |
| **SHOULD** | G11 — Neptune Analytics: extraction + rules for `CALL neptune.algo.*` and vector search without a scoping filter |
| **SHOULD** | G12 — Inferred domain graph: labels/edge labels observed in code projected as a draft domain schema linked to the system graph |
| **SHOULD** | G13 — Field cycle on a real graph-backed repo recorded in the `apiforge field` ledger; ship allowed with it declared `unresolved` |
| **COULD** | G14 — Supernode hint from declared edge-label cardinality in plan/profile dumps |

---

## Success Criteria

- [ ] Roster count = 26 agents; `apiforge agents lint` exits 0; `api-data-access-architect` toolset contains 0 `model neptune*` entries.
- [ ] Skill `api-forge-graph` has 6 reference files + 2 packs (`neptune` ≥ 8 topic files: database, analytics, loader, streams, iam-sigv4, network, snapshots, cloudwatch; `neo4j` ≥ 4: driver, cypher-dialect, indexes-constraints, plans); skills lint exits 0.
- [ ] Golden corpus: ≥ 2 positive + ≥ 1 negative case **per `AF-GRAPH-*` rule per supported language** (Python, Java, Go, TypeScript), plus `AF-DATA-013` cases for Neo4j.
- [ ] `apiforge evals graph-quality`: precision = 1.00 on Python AST cases; precision ≥ 0.90 on regex languages (Java/Go/TS); global recall ≥ 0.90; 0 false positives on bounded-query negatives; exit 1 when any threshold fails.
- [ ] `model graph-explain` parses 100% of plan fixtures (≥ 1 per format: Gremlin explain, Gremlin profile, openCypher static, openCypher dynamic, SPARQL explain, Neo4j EXPLAIN, Neo4j PROFILE = ≥ 7) into `GraphPlanIR`; a call site without a plan reports `unresolved` (never inferred).
- [ ] `collect neptune-explain`: 100% of refusal tests pass — mutation query, PROFILE without flag, PROFILE without declared reader endpoint, non-GET transport — each emitting a cataloged `AF-*` code with `field` and `unlock` in CLI and MCP output.
- [ ] Export round-trip: system-graph fixture → OpenCSV validates against Neptune bulk-loader header grammar (`~id`, `~label`, `~from`, `~to`, typed columns) and → N-Triples parses line-by-line as valid RDF 1.1 N-Triples; node/edge counts equal input counts.
- [ ] Every new `AF-*` code present in the catalog; catalog load test passes.
- [ ] `apiforge evals economy-hardening` passes; `apiforge evals agentic-quality --baseline <previous report>` shows no regression; `apiforge sdd check --root docs/sdd` exits 0.
- [ ] Full test suite green once before ship (targeted tests per wave).

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Routing hand-off | Host asks a Gremlin modeling question | Agent routing resolves the owner | `api-graph-data-architect` selected; `api-data-access-architect` not selected for graph stores |
| AT-002 | Multi-line unbounded chain | Python file with `g.V()` on one line and `.out('knows')` on the next, no `.limit` | `model graph-access` runs | Exactly one `AF-DATA-013` finding; no duplicate `AF-GRAPH-*` for the same risk |
| AT-003 | Bounded chain negative | Multi-line chain ending `.limit(10)` | Extraction runs | `bounded=true`; zero unbounded findings |
| AT-004 | `repeat()` without stop | `g.V().repeat(out())` without `times()`/`until()` | Rules run | `AF-GRAPH-*` repeat-without-stop finding with evidence ref |
| AT-005 | Open variable-length path | Neo4j Java `session.run("MATCH (a)-[*]->(b) RETURN b")` | Extraction + rules | Open-path finding, `vendor=neo4j`, `language=opencypher` |
| AT-006 | SPARQL property path | SPARQL `?s :knows+ ?o` without LIMIT | Rules run | Property-path finding + `AF-DATA-013` |
| AT-007 | TypeScript extraction | TS file using `gremlin` JS driver | Extraction runs | Call site emitted with heuristic diagnostic declared |
| AT-008 | Plan import | Synthetic Neptune Gremlin profile dump | `model graph-explain` | `GraphPlanIR` produced; fixture tagged `synthetic` in evidence |
| AT-009 | Missing plan | Call site with no imported plan | Agent asks about cardinality | Answer marked `unresolved`; no inferred plan |
| AT-010 | Collector default | Read-only Gremlin query | `collect neptune-explain` without flags | Non-executing explain request (GET), receipt written |
| AT-011 | PROFILE guard — mutation | Query containing `addV`/`CREATE`/`INSERT` | `collect neptune-explain --profile` | Refused with cataloged `AF-GRAPH-PROFILE-*`, `field`, `unlock`; no network call |
| AT-012 | PROFILE guard — reader | Read-only query, flag set, no reader endpoint declared | `collect neptune-explain --profile` | Refused with `AF-*` naming the reader-endpoint unlock |
| AT-013 | OpenCSV export | Workspace system graph fixture | `graph export --format neptune` | Vertex + edge CSV files valid under bulk-loader grammar; counts match |
| AT-014 | RDF export | Same fixture | `graph export --format rdf` | Valid N-Triples; triple count matches nodes + edges + properties |
| AT-015 | Analytics full-graph algo | `CALL neptune.algo.pageRank` with no scoping | Rules run | Analytics finding (SHOULD G11) |
| AT-016 | Eval gate | Corpus with one regressed rule | `apiforge evals graph-quality` | Exit 1, failing rule named |

---

## Out of Scope

- Numeric Neptune cost calculator (cost stays qualitative in `packs/neptune`).
- Neo4j live collector (Neo4j plans only via imported dumps).
- Any index/constraint creation or graph mutation by API Forge.
- A dedicated `api-neptune-engineer` agent (overlaps infra/architecture/observability/operations owners).
- Live connection from the core; provider SDK imports in `src/`.
- IAM/VPC/Terraform review of Neptune (stays with `api-infra-reviewer`), CloudWatch monitor projection (stays with `api-observability-integration-engineer`), timeouts/retries (stays with `api-resilience-engineer`).
- Graph vendors other than Neptune and Neo4j.

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | No provider SDK imports in `src/`; no live AWS/DB mutation from core | Collector lives with `collect` (outside core); transport mocked in tests |
| Technical | Collector GET-only, receipted; receipts never prove freshness | Receipt schema reused from existing collectors |
| Safety | PROFILE / dynamic explain execute the query | Opt-in flag + mutation detector (Gremlin `addV/addE/drop/property`, Cypher `CREATE/MERGE/SET/DELETE/REMOVE`, SPARQL `INSERT/DELETE/LOAD/CLEAR`) + declared reader endpoint |
| Governance | Every refusal keeps `AF-*` code, `field`, `unlock` in CLI and MCP; codes cataloged | New catalog area `graph` |
| Governance | Edit `agents/*.md` only, then `apiforge agents sync` + `lint`; edit `.agents/skills` only | Mirrors are generated and gated |
| Governance | New datastore specialization updates IR, agent routing and host mirrors | Part of W1 |
| Compatibility | `AF-DATA-013` ID stable | Extended, not replaced |
| Process | Targeted tests per wave; full suite once before ship; pytest basetemp `E:/afpt` | Wave-scoped test selection |
| Evidence | Synthetic fixtures labeled `synthetic`, never reported as field evidence | Replace with redacted real samples before ship |
| Process | `apiforge sdd check --root docs/sdd` before ship; update tests and SDD artifacts together | SDD artifacts under `docs/sdd/API_GRAPH_NEPTUNE` |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/apiforge/adapters/` (graph extraction, likely new `graph_/` module split from `dbaccess.py`), `src/apiforge/contracts/` (GraphAccessIR, GraphPlanIR), `src/apiforge/data_governance.py`, `src/apiforge/rules/catalog/graph.yaml`, `src/apiforge/collectors/` (neptune-explain), `src/apiforge/graph/export.py`, `src/apiforge/evals/` (graph_quality), `src/apiforge/cli.py` + `src/apiforge/mcp/tools.py`, `agents/api-graph-data-architect.md`, `.agents/skills/api-forge-graph/`, `docs/contracts/`, `tests/fixtures/graph_*` | Extends existing extractor → IR → governance → CLI/MCP pattern |
| **KB Domains** | agentspec: `data-modeling`, `aws`, `testing`, `anti-patterns`, `component-model` (no graph KB domain exists). Project: `.agents/skills/api-forge-data-access`, `api-forge-context`, `api-forge-sdd`; `docs/catalog-contract.md`; `docs/contracts/DataAccessReadiness-v1.md`; `docs/sdd/API_FORGE_GRAPH_DOCUMENT_SPECIALIZATION_7` | External ground truth: AWS Neptune user guide (explain/profile, bulk loader, Streams, Analytics), Apache TinkerPop reference, openCypher spec, W3C SPARQL 1.1, RDF 1.1 N-Triples, Neo4j Cypher manual |
| **IaC Impact** | None | Offline tool; no infrastructure created |

---

## Data Contract (if applicable)

### Source Inventory
| Source | Type | Volume | Freshness | Owner |
|--------|------|--------|-----------|-------|
| Application code | Gremlin/openCypher/SPARQL call sites | per repo | static scan at run | user repo |
| Plan dumps | Operator-imported explain/profile text/JSON | per query | operator-run | operator |
| Neptune explain endpoint | GET-only collector | per query | on demand, receipted | operator |
| Cluster dumps | `collect neptune` | per cluster | operator-run | operator |
| System graph | `graph export` input | per workspace | on demand | API Forge |

### Schema Contract
| Column | Type | Constraints | PII? |
|--------|------|-------------|------|
| `vendor` | enum `neptune\|neo4j` | NOT NULL | No |
| `language` | enum `gremlin\|opencypher\|sparql` | NOT NULL | No |
| `query_text` | string | nullable (dynamic queries) | Possible — redact literals |
| `labels_used` / `edge_labels_used` | list[string] | may be empty | No |
| `bounded` / `mutation` | bool | NOT NULL | No |
| `shape_risks` | list[enum] | may be empty | No |
| `evidence_ref` | path + line + sha256 | NOT NULL | No |

### Freshness SLAs
| Layer | Target | Measurement |
|-------|--------|-------------|
| GraphAccessIR | Regenerated on each run | input file sha256 in evidence_ref |
| GraphPlanIR | As fresh as imported dump | dump sha256 + receipt timestamp; never claimed fresh |

### Completeness Metrics
- 100% of plan fixtures parse; unparseable dump → diagnostic, not silent drop.
- Every call site has `evidence_ref`; zero facts without provenance.

### Lineage Requirements
- Finding → fact → `evidence_ref` (file/line/sha256) or dump/receipt sha256.
- Exported graph node/edge ids trace back to system-graph ids.

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | Neptune explain/profile output formats are stable enough to parse from official-doc shapes | Parser breaks on real dumps; W3 needs rework once real samples arrive | [ ] |
| A-002 | Owner's real explain/profile outputs and cluster dumps can be redacted and committed before ship | W3/W5 evidence remains `synthetic-only` at ship | [ ] |
| A-003 | Non-executing explain is reachable via HTTP GET for Gremlin, openCypher and SPARQL on Neptune | Collector needs POST → conflicts with GET-only boundary; scope down to dumps for that language | [ ] |
| A-004 | Regex extraction for Java/Go/TS can reach precision ≥ 0.90 on the corpus | Lower threshold or add AST parsing for that language | [ ] |
| A-005 | Moving `model neptune*` off `api-data-access-architect` breaks no existing routing evals | Routing evals need fixture updates | [ ] |
| A-006 | Neptune bulk-loader OpenCSV grammar can be validated offline from spec | Round-trip relies on manual check | [ ] |
| A-007 | `AF-DATA-013` can be extended to Neo4j without changing its semantics | Need a separate Neo4j unbounded code | [ ] |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | One sentence, cited evidence (file:line), concrete production impact |
| Users | 2 | Four personas with pains; no real graph-backed user repo identified (field cycle target missing) |
| Goals | 3 | 14 goals with MoSCoW, each mapped to a wave |
| Success | 3 | Numeric thresholds (precision/recall, counts, exit codes) chosen by owner |
| Scope | 3 | Explicit out-of-scope + ownership boundaries with other agents |
| **Total** | **14/15** | |

---

## Open Questions

None blocking Design. Carried as tracked risks:
- A-003 (GET reachability of non-executing explain per language) — resolve in Design from Neptune docs.
- Field cycle target repo — owner to provide; ship allowed with `unresolved`.
- Real redacted samples — owner to provide before ship.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-10-01 | define-agent | Initial version from BRAINSTORM_API_GRAPH_NEPTUNE (Approach A); thresholds "Rigoroso"; field cycle SHOULD + unresolved; AF-DATA-013 kept as single unbounded rule |
| 1.1 | 2026-10-01 | design-agent | Design corrections: rule namespace AF-GDB-* (AF-GRAPH-* is system graph); collector boundary = read-only neptunedata allowlist (explain is POST; SPARQL dump-only; owner approved); vendor knowledge in knowledge/ packs; unified fact kind data.graph.query |
| 1.2 | 2026-10-01 | ship-agent | Shipped and archived (commit 698b46b) |

---

## Next Step

**Ready for:** `/agentspec:workflow:ship .claude/sdd/features/DEFINE_API_GRAPH_NEPTUNE.md`
