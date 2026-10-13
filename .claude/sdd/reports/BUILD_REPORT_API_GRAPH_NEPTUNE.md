# BUILD REPORT: API Graph & Neptune Specialization

> Implementation report for API_GRAPH_NEPTUNE

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_GRAPH_NEPTUNE |
| **Date** | 2026-10-01 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_API_GRAPH_NEPTUNE.md](../features/DEFINE_API_GRAPH_NEPTUNE.md) |
| **DESIGN** | [DESIGN_API_GRAPH_NEPTUNE.md](../features/DESIGN_API_GRAPH_NEPTUNE.md) |
| **Status** | Complete (field cycle `unresolved` by design — SHOULD G13) |
| **Branch** | `feature/graph_evo` (base `4ebd286`, uncommitted) |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 54/55 manifest rows (row 55 field ledger: unresolved, no target repo) |
| **Files Changed** | ~234 incl. generated mirrors, corpus fixtures and pack docs |
| **Lines of Code** | src +2301 / −138; tests + evals corpus +2078 / −6 |
| **Tests Passing** | full suite 1420 passed, 1 skipped, 1 failed → fixed / explained (see Verification) |
| **Agents Used** | 1 subagent (prose: agent, skill, references) + direct build |

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Notes |
|---|------|-------|--------|-------|
| 1 | `agents/api-graph-data-architect.md` + data-access hand-off | @general-purpose (code-documenter role) | ✅ | lint 0 findings; 516 words, 282-char description |
| 2 | Skill `api-forge-graph` (SKILL.md + 9 references) + data-access skill hand-off | @general-purpose | ✅ | pt-BR like siblings; `validate_skills.py` ok |
| 3 | Mirrors (`agents sync`, `sync_skills.py`) | (direct) | ✅ | 26 agents |
| 4 | Playbook, expertise triggers | (direct) | ✅ | see Autonomous Decisions #2 |
| 5 | Knowledge packs `graph-databases`, `neo4j` (new), `neptune` (v2) | (direct) | ✅ | `knowledge check` clean |
| 6 | `rules/catalog/gdb.yaml` (16 rules) + `AF-DATA-013` rebinding | (direct) | ✅ | catalog surface test updated |
| 7 | `contracts/graph_access.py` + registry | (direct) | ✅ | |
| 8 | `adapters/graph_/{gremlin,cypher,sparql,extract,ir,plans}.py` | (direct) | ✅ | Python AST + Java/Go/TS patterns |
| 9 | `dbaccess.py` Neptune removal + compat wrapper | (direct) | ✅ | |
| 10 | `data_governance.py`, `stubs.py` (neo4j) | (direct) | ✅ | |
| 11 | `collectors/graph_explain.py` | (direct) | ✅ | allowlist + guards |
| 12 | `graph/formats.py`, `graph/export.py`, `contracts/graph.py` | (direct) | ✅ | Gremlin CSV + N-Triples |
| 13 | `evals/graph_quality.py` + corpus (85 cases) + thresholds | (direct) | ✅ | |
| 14 | CLI + dispatch verbs | (direct) | ✅ | |
| 15 | Tests (analyzers, extract, plans, collector, export, eval) | (direct) | ✅ | 6 new test files |
| 16 | Docs: README, CLAUDE.md, AGENTS.md, catalog-contract, 2 contract docs | (direct) | ✅ | |
| 17 | Routing corpus (+6 graph cases) | (direct) | ✅ | |
| 18 | `docs/sdd/API_GRAPH_NEPTUNE` chain discover→benchmark + evidence | (direct) | ✅ | ship.md left for /ship |
| 19 | Field cycle ledger | — | ⏳ unresolved | no graph-backed target repo |

---

## Agent Contributions

| Agent | Files | Specialization Applied |
|-------|-------|------------------------|
| @general-purpose (prose) | 12 | agent/skill contracts, AWS/TinkerPop/W3C/Neo4j sources |
| (direct) | rest | DESIGN patterns 1-8, repo conventions (extractor → IR → catalog → CLI/MCP) |

DESIGN assigned agentspec specialists (python-developer, test-generator, code-documenter, aws-data-architect). Code was built directly to keep `cli.py`/`runner.py` edits sequential and conflict-free; only independent prose was delegated.

---

## Verification Results

### Lint Check

```text
ruff check src tests: All checks passed
ruff format --check src tests: 851 files already formatted
```

**Status:** ✅ Pass

### Type Check

```text
mypy src/apiforge: Success: no issues found in 473 source files
```

**Status:** ✅ Pass

### Tests

```text
full suite (--basetemp E:/afpt/full2): 1420 passed, 1 skipped, 1 failed
  failed: test_check_release::test_release_gate_accepts_complete_repository
    - GraphAccessIR/v1, GraphPlanIR/v1 docs unregistered  -> fixed (contracts/registry.py)
    - untracked .claude/agents/README.md (pre-existing, not part of this change)
  rerun tests/scripts + tests/contracts: 76 passed, 1 failed (the pre-existing file only)
  release gate with that file moved aside: PASS (file restored afterwards)
```

| Gate | Result |
|------|--------|
| `apiforge evals graph-quality` | ✅ 85 cases, precision 1.0 (py/java/go/ts), recall 1.0, bounded FP 0 |
| `apiforge agents lint` | ✅ 26 agents, 0 findings |
| `scripts/validate_skills.py` | ✅ |
| `apiforge knowledge check` | ✅ problems [] |
| `apiforge evals agent-routing` | ✅ 81 cases top1 0.9753 (baseline 75 cases 0.9733); 6/6 graph cases |
| `apiforge evals agentic-quality --baseline` | ✅ accuracy 1.0 = baseline (HEAD worktree) |
| `apiforge evals economy-hardening` | ✅ 18 cases |
| `apiforge sdd check --root docs/sdd` | ⏳ only `AF-SDD-PHASE-SKIPPED-UNDECLARED` for `ship` (next phase) |

**Status:** ✅ (with the pre-existing untracked file noted)

---

## Issues Encountered

| # | Issue | Resolution |
|---|-------|------------|
| 1 | `AF-GRAPH-*` taken by system-graph refusals | `AF-GDB-*` (design C1) |
| 2 | Go `gremlingo` PascalCase normalized `V`→`v` | single-letter steps kept; snake_case (`gremlin_python`) also canonicalized |
| 3 | `topKByEmbedding` contains "topk" → false negative | require a `topK:` parameter; only `vectors.topK*` checked |
| 4 | Neptune explain "not converted" list duplicated and split on inner commas | Optimized section only; top-level split |
| 5 | Neo4j `\| \| +Op` rows mis-split | column positions from header bars |
| 6 | Holdout: Gremlin chain inside a Java comment became a fact | `blank_comments` before pattern scans |
| 7 | One regressed case hidden by global recall | per rule × language gates added |
| 8 | Eval took 22 s (tempdir per case) | single extraction grouped by file: 1.3 s |
| 9 | `Path.write_text` produced CRLF on Windows | normalized all touched files to LF (repo convention) |
| 10 | `gen_pack_docs.py` rewrote 31 unrelated packs (pre-existing drift) | reverted unrelated packs; only graph packs regenerated |
| 11 | Release gate: new contract docs unregistered | registered in `contracts/registry.py` |

---

## Autonomous Decisions

| # | Decision Point | Options Considered | Chose | Rationale |
|---|----------------|--------------------|-------|-----------|
| 1 | Who writes code vs prose | delegate per manifest vs direct | prose delegated, code direct | shared `cli.py`/`runner.py`; avoid parallel edit conflicts |
| 2 | `api-graph-review` capability in agentic runtime | add vs skip | skip (profile reverted) | default specialist fan-out would change economy baselines; agent uniqueness already from area `GDB` |
| 3 | Gremlin CSV naming | "OpenCSV" vs loader `csv` format | "Neptune Gremlin CSV" | `~id/~label/~from/~to` is the Gremlin load format (subagent flag, verified) |
| 4 | Neptune Analytics extraction | none vs boto3 `neptune-graph.execute_query(queryString=)` | boto3 path, Python only | needed to make AF-GDB-009/010 observable; other languages use SDK builders |
| 5 | Edge properties in N-Triples | reify vs omit | omit (documented) | no reification vocabulary declared; counts stay exact |
| 6 | Mutation in DataAccessIR | per-verb tokens vs `command: mutation` | `command: mutation` | reuses `build_data_access_ir` pattern fields; Cypher/SPARQL mutations reach readiness blockers |
| 7 | `--profile` with dynamic text | allow vs refuse | refuse `AF-GDB-PROFILE-DYNAMIC` | executing plans need provable read-only text |
| 8 | SPARQL `executed` | fixed false vs derived | derived from runtime columns | SPARQL dynamic/details run the query |
| 9 | Unrelated pack doc drift | commit regenerated vs revert | revert | scope discipline; drift predates this change |
| 10 | `.claude/agents/README.md` failing release gate | delete vs leave | leave, report | untracked file existed before the session; not ours to delete |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| No `api-graph-review` agent profile | Decision #2 | none on routing (6/6) |
| TypeScript scanning also covers `.js/.mjs/.tsx` | same driver APIs | broader coverage, same heuristic diagnostic |
| `AF-GRAPH-EXPORT-INVALID` added | export refuses a projection failing its grammar | new cataloged code |
| `GraphExport.files` field | design called for per-file digests in export.json | optional, default `()` |
| `ship.md` not created | belongs to /ship | `sdd check` names it |

---

## Blockers (if any)

| Blocker | Required Action | Owner |
|---------|-----------------|-------|
| Field cycle (SHOULD G13) | point `apiforge field` at a real Neptune/Neo4j-backed repo | owner |
| Real plan samples (A-002) | redact and commit real explain/profile dumps + cluster dumps; replace synthetic fixtures | owner |
| Pre-existing untracked `.claude/agents/README.md` | commit it into the mirror contract or remove it | owner |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|----|----------|--------|----------|
| AT-001 | Routing hand-off | ✅ | agent-routing R076–R081 top-1 `api-graph-data-architect` |
| AT-002 | Multi-line unbounded chain → one AF-DATA-013 | ✅ | `test_multiline_python_chain_unbounded_fires_once` |
| AT-003 | Bounded chain negative | ✅ | `test_multiline_python_chain_is_one_bounded_fact` |
| AT-004 | `repeat()` without stop | ✅ | `test_repeat_without_stop_fires` |
| AT-005 | Neo4j Java open path | ✅ | `test_java_neo4j_open_path` |
| AT-006 | SPARQL property path + no LIMIT | ✅ | corpus `python/s-path-unbounded` (AF-GDB-007 + AF-DATA-013) |
| AT-007 | TypeScript extraction + heuristic diag | ✅ | `test_typescript_gremlin_and_heuristic_diagnostic` |
| AT-008 | Plan import, synthetic flag | ✅ | `test_every_fixture_parses_and_judges` |
| AT-009 | Missing plan → unresolved | ✅ | `test_dynamic_query_is_unresolved_not_guessed`; plan refusal tests |
| AT-010 | Collector default non-executing | ✅ | `test_default_gremlin_is_non_executing_explain`, `test_default_cypher_is_static` |
| AT-011 | PROFILE mutation refused, no network | ✅ | `test_refusals_never_touch_the_client` |
| AT-012 | PROFILE without reader refused | ✅ | same parametrized test |
| AT-013 | Gremlin CSV export | ✅ | `test_neptune_csv_round_trip` |
| AT-014 | RDF export | ✅ | `test_rdf_round_trip` |
| AT-015 | Analytics unscoped algo | ✅ | `test_cypher_analytics_and_vectors`; corpus `a-unscoped*` |
| AT-016 | Eval gate on regression | ✅ | `test_regressed_case_fails_and_names_rule` |

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Precision Python AST | 1.00 | 1.00 | ✅ |
| Precision Java/Go/TS | ≥ 0.90 | 1.00 / 1.00 / 1.00 | ✅ |
| Global recall | ≥ 0.90 | 1.00 | ✅ |
| Bounded false positives | 0 | 0 | ✅ |
| Cases per rule × language | ≥ 2 pos + 1 neg | met (coverage gate empty) | ✅ |
| Plan fixtures parsed | 7/7 | 7/7 | ✅ |

Caveat: the golden corpus was authored with the code (in-distribution). Six holdout cases found one real bug before passing; scores of 1.0 do not prove generalization — the field cycle stays the real test.

---

## Final Status

### Overall: ✅ COMPLETE (field cycle unresolved, by DEFINE decision)

- [x] All tasks from manifest completed (except field ledger)
- [x] All verification checks pass
- [x] All tests pass (one release-gate failure is a pre-existing untracked file)
- [x] No blocking issues for ship
- [x] Acceptance tests verified (16/16)
- [x] Ready for /ship

---

## Next Step

**If Complete:** `/agentspec:workflow:ship .claude/sdd/features/DEFINE_API_GRAPH_NEPTUNE.md`
