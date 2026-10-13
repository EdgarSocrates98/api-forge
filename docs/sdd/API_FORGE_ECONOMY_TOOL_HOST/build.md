---
sdd: 1
feature: API_FORGE_ECONOMY_TOOL_HOST
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "6f27cf0afdb9bc58d4f81844dca30d22e9fddb6adf835314358bab12b687e7e0"
tasks:
- id: contracts
  status: done
  evidence: sdd/API_FORGE_ECONOMY_TOOL_HOST/evidence/tool-host-tests.txt
- id: output
  status: done
  evidence: sdd/API_FORGE_ECONOMY_TOOL_HOST/evidence/tool-host-tests.txt
- id: slicers
  status: done
  evidence: sdd/API_FORGE_ECONOMY_TOOL_HOST/evidence/tool-host-tests.txt
- id: mcp
  status: done
  evidence: sdd/API_FORGE_ECONOMY_TOOL_HOST/evidence/tool-host-tests.txt
- id: hosts
  status: done
  evidence: sdd/API_FORGE_ECONOMY_TOOL_HOST/evidence/tool-host-tests.txt
- id: eval
  status: done
  evidence: sdd/API_FORGE_ECONOMY_TOOL_HOST/evidence/tool-economy-eval.json
claims:
- compact-output
- test-slice
- error-slice
- gateway-mcp
- surface-measurement
- host-projection
- tool-economy-eval
---
# build

Implemented `--output`, `slice tests|log`, `mcp surface`, `agentops projection`, `apiforge-mcp --surface/--host` and `apiforge evals tool-economy`, with MCP parity for the new verbs.
