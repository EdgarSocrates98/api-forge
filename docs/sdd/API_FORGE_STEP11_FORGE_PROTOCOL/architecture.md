---
sdd: 1
feature: API_FORGE_STEP11_FORGE_PROTOCOL
phase: architecture
profile: critical
status: done
files:
  - src/apiforge/contracts/forge_protocol.py
  - src/apiforge/contracts/registry.py
  - src/apiforge/contracts/__init__.py
  - src/apiforge/forge/__init__.py
  - src/apiforge/forge/protocol.py
  - src/apiforge/forge/store.py
  - src/apiforge/cli_forge.py
  - src/apiforge/cli.py
  - src/apiforge/mcp/tools.py
  - src/apiforge/rules/forge_protocol.yaml
  - src/apiforge/evals/forge_protocol.py
  - evals/corpus/forge-protocol/
  - tests/forge/test_protocol.py
  - tests/mcp/test_tools.py
  - docs/architecture/forge-kernel-boundary.md
  - docs/contracts/Forge*-v1.md
  - docs/catalog-contract.md
decisions:
  - "forge tasks live under .apiforge/forge/ — separate from governed tasks, linked only via attach"
  - "capability matrix is derived from declared contracts/agents — public, versioned, never invented"
  - "risk gate list lives in rules/forge_protocol.yaml — policy is declared data"
  - "handoff targets are a declared engine allowlist — undeclared peers refuse"
  - "governed projection maps TaskSpec state to Forge state; unresolved projections name their gap"
  - "MCP exposes only the read plane — submit/attach/handoff stay CLI verbs"
upstream:
  path: contract.md
  sha256: "80a735ffe0905673a183a10181d1c33b3895b60e15da51691dfb9de651f0fb15"
---

# architecture

`contracts/forge_protocol.py` defines the eight wire contracts.
`forge/store.py` persists task rows + handoffs as contract-validated JSON
under `.apiforge/forge/`. `forge/protocol.py` implements the lifecycle:
`discover_capabilities` reads the declared matrix, `submit_task` runs the
capability + risk gates and persists, `attach_task` links a governed
TaskSpec id, `inspect_task`/`retrieve_result`/`retrieve_evidence` project
governed state and artifacts with explicit gaps, `prepare_handoff` emits
a prepared record for declared engines only, `health` reports wire
identity + task counts. `cli_forge.py` exposes all verbs; `mcp/tools.py`
adds five read-only projections.
