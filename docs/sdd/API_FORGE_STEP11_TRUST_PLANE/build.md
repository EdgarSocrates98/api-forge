---
sdd: 1
feature: API_FORGE_STEP11_TRUST_PLANE
phase: build
profile: critical
status: done
upstream:
  path: plan.md
  sha256: "33b9f46160535e07705f8132491efea5ca83297e98efc9529e703e455bff2a73"
tasks:
  - id: B1
    summary: contracts + widened literals + registry + contract docs
    files: [src/apiforge/contracts/trust.py, src/apiforge/contracts/agentic_memory.py, src/apiforge/contracts/registry.py, src/apiforge/contracts/__init__.py]
  - id: B2
    summary: trust plane annotation, propagation, tool authorization, risk yaml
    files: [src/apiforge/trust/plane.py, src/apiforge/trust/propagation.py, src/apiforge/trust/tools.py, src/apiforge/rules/tool_risk.yaml]
  - id: B3
    summary: memory gates, quarantine, ranking, invalidation, parity test, CLI/MCP
    files: [src/apiforge/memory/security.py, src/apiforge/memory/retrieval.py, src/apiforge/memory/invalidation.py, src/apiforge/memory/store.py, src/apiforge/cli_agentic_state.py, src/apiforge/mcp/tools.py]
claims:
  - DATA IS NOT INSTRUCTION is enforced by the TrustUnit validator and by
    MemoryTrust.instruction_authority being a Literal["none"] on memory rows
  - every runnable registry tool carries a declared risk profile and every
    role grant is allowlist-first with cataloged denials
  - trust-insufficient candidates quarantine, stay invisible to retrieval and
    release only through a re-run of the full gate pipeline
  - checkpoint parity is proven: resumed state equals continuous state
---

# build

Implemented on `evo/step11-agentic-closure`:

- `src/apiforge/contracts/trust.py` — 11 contracts + closed literals;
  `TrustUnit` validator enforces DATA IS NOT INSTRUCTION.
- `src/apiforge/contracts/agentic_memory.py` — `MemoryOrigin` +`knowledge`,
  `MemoryState`/`MemoryAction` +`quarantined` (additive).
- `src/apiforge/trust/{plane,propagation,tools}.py` + `rules/tool_risk.yaml`.
- `src/apiforge/memory/{security,retrieval,invalidation}.py`; `store.py`
  rewired onto the gate pipeline + `quarantine.jsonl` + `review_quarantine`.
- CLI: `memory rank`, `memory quarantine-list`, `memory quarantine-resolve`;
  MCP tools `memory_rank`, `memory_quarantine_list`,
  `memory_quarantine_resolve`.
- Tests: 39 new tests across contracts, trust plane, propagation, tools,
  memory security/retrieval/invalidation and checkpoint parity — 47 total
  with the unchanged pre-existing suite.
- Docs: 11 contract pages, catalog codes, `API_FORGE_AGENTIC_STATE.md`
  (quarantine + §18 four-compactions distinction), README rows.
