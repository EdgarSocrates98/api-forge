---
sdd: 1
feature: API_FORGE_STEP11_FORGE_PROTOCOL
phase: build
profile: critical
status: done
tasks:
  - id: B1
    summary: eight contracts + registry + exports + catalog codes + contract docs + rules file
    files: [src/apiforge/contracts/forge_protocol.py, src/apiforge/contracts/registry.py, src/apiforge/contracts/__init__.py, src/apiforge/rules/forge_protocol.yaml, docs/contracts/, docs/catalog-contract.md]
  - id: B2
    summary: forge store + protocol lifecycle (submit/attach/inspect/result/evidence/handoff/health/capabilities)
    files: [src/apiforge/forge/__init__.py, src/apiforge/forge/store.py, src/apiforge/forge/protocol.py]
  - id: B3
    summary: forge CLI group + 5 read-only MCP tools + boundary doc + eval + corpus + tests
    files: [src/apiforge/cli_forge.py, src/apiforge/cli.py, src/apiforge/mcp/tools.py, docs/architecture/forge-kernel-boundary.md, src/apiforge/evals/forge_protocol.py, evals/corpus/forge-protocol/, tests/forge/test_protocol.py, tests/mcp/test_tools.py]
claims:
  - "submit refuses unknown capabilities, unacknowledged gated risk and duplicate ids; unknown engine refuses at handoff"
  - "result projects governed outcomes honestly — missing attach yields unresolved with named gaps, invalid DONE proof yields review"
  - "evidence bundles carry observed artifacts only (request/status/ledger/governed) plus an explicit unresolved list"
  - "handoff emits prepared ForgeHandoff records for declared peers; delivery is an out-of-band human boundary"
upstream:
  path: plan.md
  sha256: "49dc9011a1a5db6b59f1abf1c2a2f5048191b0690b8c2069cb5963695fa10403"
---

# build

All modules are additive; no existing contract, store or verb was
reshaped. The governed runtime is reused through `taskspec.store` and
`brief_for_task` — the forge layer never re-implements lifecycle logic.
