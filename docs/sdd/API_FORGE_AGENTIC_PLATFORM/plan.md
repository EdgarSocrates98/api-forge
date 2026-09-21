---
sdd: 1
feature: API_FORGE_AGENTIC_PLATFORM
phase: plan
profile: critical
status: ready
upstream:
  path: architecture.md
  sha256: "9e64ba437ec6af7d58abec9ed907a6339e971f878ca61df81a0fc810ae44f877"
tasks:
  - id: A1
    covers: [contracts-v1]
    test: sdd/API_FORGE_AGENTIC_PLATFORM/evidence/A1.txt
  - id: A2
    covers: [contracts-v1]
    test: sdd/API_FORGE_AGENTIC_PLATFORM/evidence/A2.txt
  - id: B1
    covers: [task-verbs]
    test: sdd/API_FORGE_AGENTIC_PLATFORM/evidence/B1.txt
  - id: B2
    covers: [task-verbs]
    test: sdd/API_FORGE_AGENTIC_PLATFORM/evidence/B2.txt
  - id: B3
    covers: [brief-done-refusal]
    test: sdd/API_FORGE_AGENTIC_PLATFORM/evidence/B3.txt
  - id: C1
    covers: [graph-verbs]
    test: sdd/API_FORGE_AGENTIC_PLATFORM/evidence/C1.txt
  - id: C2
    covers: [graph-verbs]
    test: sdd/API_FORGE_AGENTIC_PLATFORM/evidence/C2.txt
  - id: D1
    covers: [extractor-cache]
    test: sdd/API_FORGE_AGENTIC_PLATFORM/evidence/D1.txt
  - id: D2
    covers: [extractor-cache]
    test: sdd/API_FORGE_AGENTIC_PLATFORM/evidence/D2.txt
  - id: E1
    covers: [e2e-slice]
    test: sdd/API_FORGE_AGENTIC_PLATFORM/evidence/E1.txt
  - id: F1
    covers: [contracts-v1, task-verbs, brief-done-refusal, graph-verbs, extractor-cache]
    test: sdd/API_FORGE_AGENTIC_PLATFORM/evidence/F1.txt
---

# plan

Atomic tasks A1 -> F1 in dependency order. `covers` references the intent
success ids; `test` points at the captured pytest output committed under
`evidence/` when the task lands (until then the check reports it as an
unresolved gap, not a refusal).

| Task | Scope |
|---|---|
| A1 | contracts registry + versioned models + conformance tests + `contract list/show` |
| A2 | `version` field on Fact/Finding/Receipt, backward compat |
| B1 | taskspec store + state machine + transitions in history.jsonl |
| B2 | Ed25519 seal + recipes + budgets + no-progress breaker + run |
| B3 | OutcomeBrief render + DONE refusals |
| C1 | graph build + canonical store + deterministic bytes |
| C2 | query/impact/trace/coverage/export |
| D1 | sha256 cache over extractors + economy `cache_hit` |
| D2 | `index build/status` (files/symbols/routes/facts) |
| E1 | e2e slice: build endpoint wrapped in task + brief + evidence |
| F1 | docs (catalog-contract, threat model), gate parity, MCP parity for new verbs |
