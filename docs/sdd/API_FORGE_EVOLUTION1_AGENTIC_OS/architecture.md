---
sdd: 1
feature: API_FORGE_EVOLUTION1_AGENTIC_OS
phase: architecture
profile: critical
status: ready
upstream:
  path: contract.md
  sha256: "62ed1555f44e62a58b764452e36e225e8bdf80ce784a584de10fc1b3bf74eac8"
files:
  - src/apiforge/contracts/agentic_memory.py
  - src/apiforge/memory/store.py
  - src/apiforge/blackboard/store.py
  - src/apiforge/runtime/semantic_checkpoint.py
  - src/apiforge/cli_agentic_state.py
  - src/apiforge/mcp/tools.py
decisions:
  - id: append-only-local
    summary: store state locally as JSONL/JSON under .apiforge
    rollback: remove the additive commands and ignore state directories; no external state was mutated
  - id: evidence-gated-promotion
    summary: candidates are separate from persistent memory and cross-task promotion needs evidence
    rollback: disable persist verbs while keeping candidate artifacts readable
  - id: explicit-taint
    summary: external/model data is data with visible taint and no instruction authority
    rollback: keep entries but require human review for consumers
  - id: service-parity
    summary: CLI and MCP call the same pure local application services
    rollback: remove surface registration; canonical contracts and stores remain reusable
---

# architecture

The data plane is deliberately below CLI/MCP and above the existing case and
runtime stores. It does not import provider SDKs or model clients. Memory
retrieval is lexical and bounded; semantic/vector retrieval is deferred until
its own benchmark. The environment fingerprint is a hard filter, not a hint.

