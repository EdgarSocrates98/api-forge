---
sdd: 1
feature: API_FORGE_ECONOMY_TOOL_HOST
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "94554e94a2d0470b8edef524a3bc7d2ffe74e3e9c4acb4ffb429f83c6813e5cb"
tasks:
- id: contracts
  covers:
  - TestSlice/v1
  - ErrorSlice/v1
  - ToolSurface/v1
  - HostProjection/v1
  test: sdd/API_FORGE_ECONOMY_TOOL_HOST/evidence/tool-host-tests.txt
  risk: low
  rollback: remove contracts/tool_host.py
- id: output
  covers:
  - compact-output
  test: sdd/API_FORGE_ECONOMY_TOOL_HOST/evidence/tool-host-tests.txt
  risk: low
  rollback: --output json
- id: slicers
  covers:
  - test-slice
  - error-slice
  test: sdd/API_FORGE_ECONOMY_TOOL_HOST/evidence/tool-host-tests.txt
  risk: low
  rollback: remove agentops/slicing.py
- id: mcp
  covers:
  - gateway-mcp
  - surface-measurement
  test: sdd/API_FORGE_ECONOMY_TOOL_HOST/evidence/tool-host-tests.txt
  risk: low
  rollback: --surface full
- id: hosts
  covers:
  - host-projection
  test: sdd/API_FORGE_ECONOMY_TOOL_HOST/evidence/tool-host-tests.txt
  risk: low
  rollback: remove host_projections.yaml
- id: eval
  covers:
  - tool-economy-eval
  test: sdd/API_FORGE_ECONOMY_TOOL_HOST/evidence/tool-economy-eval.json
  risk: low
  rollback: remove evals/tool_economy.py and the corpus
---
# plan

Contracts, renderer and root option, slicers, gateway and surface, host table, surfaces, eval.
