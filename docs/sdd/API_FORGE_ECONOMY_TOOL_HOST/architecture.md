---
sdd: 1
feature: API_FORGE_ECONOMY_TOOL_HOST
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "a4390f185f3b3c3aaf02a79d929b2cf98873e163bbe2e20e7db08e1fa33b250d"
files:
- src/apiforge/contracts/tool_host.py
- src/apiforge/output/render.py
- src/apiforge/agentops/slicing.py
- src/apiforge/agentops/projection.py
- src/apiforge/mcp/gateway.py
- src/apiforge/mcp/surface.py
- src/apiforge/mcp/server.py
- src/apiforge/mcp/main.py
- src/apiforge/rules/host_projections.yaml
- src/apiforge/cli_tool_host.py
- src/apiforge/evals/tool_economy.py
decisions:
- id: prune-and-minify
  decision: compact removes only null/empty values and indentation
  rollback: --output json
- id: gateway-dispatch
  decision: apiforge_call dispatches to any registered full tool; discover ranks by tokens
  rollback: --surface full
- id: signature-schemas
  decision: surface cost measured from signatures with pydantic, no mcp extra required
  rollback: none needed
- id: never-trim-failures
  decision: slicers bound context lines only; every failure and signature is emitted
  rollback: none needed
- id: doctype-refused
  decision: JUnit XML with a DOCTYPE is refused before parsing
  rollback: none needed
- id: declared-hosts
  decision: host behavior is declared data; the core never branches on host
  rollback: remove host_projections.yaml
---
# architecture

Projections sit around the core: CLI renderer, MCP gateways and surface meter, slicers writing to the ctx CAS, and a host table resolved by the MCP entry point.
