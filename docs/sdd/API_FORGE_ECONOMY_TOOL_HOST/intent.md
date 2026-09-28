---
sdd: 1
feature: API_FORGE_ECONOMY_TOOL_HOST
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "395dc247d216129b8b8f9158e9acc66cd4c1b85db24e3a8be341fa998a126c4b"
problem: Hosts pay transport for pretty JSON, an unmeasured full MCP surface and raw test/CI logs, with
  no host-specific projection.
success:
- compact-output
- test-slice
- error-slice
- gateway-mcp
- surface-measurement
- host-projection
- tool-economy-eval
out_of_scope:
- test-selection
- verification-ladder
- yaml-output
- live-host-probing
owner: api-forge-economy
risk_class: low
risk_signals:
- path:src/apiforge/cli.py
- path:src/apiforge/mcp/server.py
- path:src/apiforge/agentops/slicing.py
---
# intent

Deliver the same evidence for fewer bytes: compact payloads, sliced logs and a gateway MCP surface chosen per host, each measured against its full form.
