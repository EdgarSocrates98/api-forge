---
sdd: 1
feature: API_FORGE_ECONOMY_TOOL_HOST
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "ceca5a10899f88bbe4e684a21fb22375fbb0be8fe635cba53b0c749c3eccaf7b"
covers:
- TestSlice/v1
- ErrorSlice/v1
- ToolSurface/v1
- HostProjection/v1
api_ir:
  input: CLI payloads, test and CI logs, MCP tool functions, host table
  output: compact payloads, slices with ctx refs, surface costs, host projections
---
# contract

No existing contract changes. `--output json` remains the default and byte-identical; the full MCP surface remains the default.
