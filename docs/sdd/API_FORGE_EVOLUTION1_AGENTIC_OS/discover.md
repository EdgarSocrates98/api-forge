---
sdd: 1
feature: API_FORGE_EVOLUTION1_AGENTIC_OS
phase: discover
profile: critical
status: done
approaches:
  - id: rewrite
    summary: replace the existing deterministic and evidence-first runtime
    verdict: refused -- destroys compatibility and duplicates shipped abstractions
  - id: parallel-subsystem
    summary: add an independent agentic platform beside the current runtime
    verdict: refused -- creates split truth and incompatible state stores
  - id: governed-evolution
    summary: extend existing contracts, case, context, runtime and MCP surfaces
    verdict: chosen -- additive, offline-first and evidence-preserving
chosen: governed-evolution
---

# discover — Phase 0 baseline and architecture assessment

## Evidence boundary

The persisted API Forge case is `.apiforge/case/case.json` with id
`case:a73685c5a5038739`. The deterministic analysis used the FastAPI fixture
`tests/fixtures/orders_agentic` and confirmed the framework explicitly as
`fastapi`. It produced four confirmed contract findings, all backed by
`fact:9d8ccab5f18594a0`, `fact:fc9d9328ab25268d`, `fact:38c019c50cd7b30e` or
`fact:2101b56405f8a180`; it produced no diagnostics or unresolved extraction
items for that fixture. Those findings are baseline evidence for the case, not
claims about this repository's production API.

## Capability matrix

| Capability | Current state | Production path | Tested/evaluated | Observable/evidence | Gap / action |
|---|---|---|---|---|---|
| Context | implemented: scoped capsules, refs, budgets, cache and funnel | CLI + MCP | tests/context, economy evals | ctx refs, hashes, economy ledger | add role-aware memory visibility |
| Runtime | implemented: bounded supervisor, routing, review, fallback | local runtime | tests/runtime | run artifacts, checkpoints, receipts | unify semantic checkpoint with economy checkpoint |
| Routing | implemented: deterministic routing, scorecards and shadow mode | CLI/runtime | tests/runtime, routing evals | routing and scorecard records | separate capability routing from model routing contract |
| Agent profiles/roles | implemented: roster, role context and playbooks | dispatch/runtime | tests/agents, runtime | playbook and dispatch records | policy needs explicit artifact/tool/memory visibility |
| Knowledge | implemented: local packs, retrieval and freshness | offline CLI/MCP | tests/knowledge, extras eval | pack fingerprints and refs | add conflict/staleness propagation into context selection |
| Evidence | implemented: case hashes, evidence graph and receipts | local control plane | tests/evidence, report | sha256 receipts and fact ids | bind memory and blackboard entries to evidence refs |
| Economy | implemented: byte ledger, token transcript adapters, profiles and phase budgets | local runtime | tests/economy | observed vs unresolved accounting | add hierarchical token/cost enforcement |
| Evals | implemented: deterministic golden/holdout/economy suites | CI/local | tests/evals | reports and gates | add memory/security/context-quality corpora |
| Observability | implemented: normalized OTel JSON, SLOs, health and provider-neutral records | offline adapters | tests/observability | telemetry snapshots | add GenAI task/agent/tool semantic projection |
| MCP | implemented: compact gateway plus full tool surface | optional MCP extra | tests/mcp | surface/parity checks | publish compliance matrix and trust metadata |
| Security/policy | implemented: policy catalog, sandbox, allowlist and refusal codes | local by default | tests/policy/security | policy decisions and named refusals | add trust/taint and per-agent tool risk profiles |
| Sandbox/promotion | implemented: copy sandbox and evidence-gated promotion | local worktree path | tests/sandbox | diffs and receipts | keep every generated artifact outside main tree until approval |
| Handoff/resume/state | partial: task history and economy checkpoints | local runtime | tests/taskspec/economy | history/checkpoint JSON | add semantic checkpoints and safe resume equivalence |
| Memory/blackboard | not observed as a first-class subsystem | none | no dedicated corpus | no canonical records | Phase 1: append-only governed stores |

## Spark Forge comparison

The benchmark repository demonstrates the same core principles that matter for
this evolution: extract facts before judging, separate provider/model costs,
use a case as the handoff bus, keep blackboard decisions evidence-bound, and
refuse ungrounded claims. API Forge already has stronger API-specific contract,
graph, sandbox, multi-language and platform surfaces. The useful concepts to
absorb are therefore the explicit blackboard/memory boundary and the
artifact-first agent layer; Spark Forge's Spark-specific extractors and
platform assumptions remain out of scope.

## Phase 0 decision

Start with an additive Phase 1 vertical slice: versioned memory and blackboard
contracts, append-only local stores, trust/taint checks, semantic checkpoint
records, CLI/MCP read and write surfaces, focused tests/evals and operational
documentation. Later phases are deliberately not promoted by this audit:
budgets, security, retrieval, OTEL, MCP/A2A compliance and live-model evals
remain separately gated work.

