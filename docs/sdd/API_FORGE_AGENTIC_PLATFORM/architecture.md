---
sdd: 1
feature: API_FORGE_AGENTIC_PLATFORM
phase: architecture
profile: critical
status: ready
upstream:
  path: contract.md
  sha256: "22e058d8657334d2ea4def28d74e0a6200cbd5c2ac0ba79e2a5ecf26fe216b0a"
files:
  - src/apiforge/contracts/ (versioned pydantic models + registry)
  - docs/contracts/<name>-v1.md + tests/contracts/
  - src/apiforge/taskspec/ (states, recipes, seal, acceptance)
  - src/apiforge/brief/ (OutcomeBrief rendering + DONE refusals)
  - src/apiforge/graph/ (JSONL store + build/query/impact/trace/coverage/export)
  - src/apiforge/index/ (file/symbol/route/fact indexes + sha256 cache)
  - src/apiforge/cli.py (task, brief, contract, graph, index verb groups)
  - rules/recipes.yaml (recipe -> verb sequence, as data)
decisions:
  - id: jsonl-graph
    choice: canonical sorted JSONL (nodes.jsonl, edges.jsonl) as the graph source of truth; queries rebuild in memory
    rollback: swap store behind the repository protocol; verbs unchanged
  - id: ed25519-task-seal
    choice: task seals reuse report/keys.py Ed25519 instead of HMAC -- seal covers the exact revision hash; `task seal` is a verb distinct from `task run`
    rollback: drop seal fields from TaskRevision; acceptance still works via Acceptancerecord
  - id: cache-by-content
    choice: cache key = sha256(source_bytes)+extractor_version; invalidation is implicit (new content = new key); stale entries are garbage, named by `index status`
    rollback: delete .apiforge/cache/ -- extractors recompute
  - id: stub-contracts
    choice: TelemetryEvent/PerformanceRun/DataAccessIR/RuntimeMatrix enter as stubs (version+identity+provenance+unresolved), not invented fields
    rollback: extend the stub in place; versioned fields only grow
  - id: brief-done-refusal
    choice: DONE is refused by the validator when mandatory gaps exist -- not advisory
    rollback: downgrade refusals to warnings (never recommended)
---

# architecture

Four sub-deliveries, each independently shippable:

1. **contracts** -- closed pydantic models under `apiforge/contracts/`, a
   `CONTRACTS` registry (`name -> class`), `docs/contracts/*-v1.md`,
   conformance tests. Existing core models gain `version: Literal[1]`.
2. **taskspec** -- `tasks/<id>/task.yaml` + `revisions/` + `history.jsonl`.
   State machine draft->reviewed->sealed->ready->running->
   parked|awaiting_supervision->accepted|rejected|blocked|expired.
   Recipes in `rules/recipes.yaml` map to verb sequences the dispatch
   runner already executes. Budgets and a no-progress breaker bound every
   run.
3. **graph** -- `graph build` reads facts/findings/contracts/rules/tasks and
   emits canonical `nodes.jsonl`/`edges.jsonl`; query verbs are pure
   functions over the store. Edge vocabulary is the closed prompt list.
4. **index** -- `index build` writes canonical `files/symbols/routes/
   facts.jsonl` derived from existing extractors; extractor results are
   cached by content hash; hits are recorded in the economy ledger.
