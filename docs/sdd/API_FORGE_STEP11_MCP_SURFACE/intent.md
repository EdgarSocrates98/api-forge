---
sdd: 1
feature: API_FORGE_STEP11_MCP_SURFACE
phase: intent
profile: critical
status: done
risk_class: medium
problem: 143 tools are exposed without measured hygiene — no audit of
  schema/description cost, no task-aware disclosure, no bounded output
  contract, no response-cost benchmark and no spec-compliance record
success: "mcp audit emits ToolSurfaceAudit over the measured surface with
  evidence-labeled findings; mcp disclose routes a task to a declared
  tool set or honestly falls back; ToolPage/paged bounds list outputs;
  mcp benchmark ranks tools by measured bytes + labeled token estimate;
  docs/mcp-compliance.md records the 12-axis matrix vs spec 2025-11-25"
out_of_scope:
  - streamable HTTP transport (stdio is the declared local transport)
  - MCP resources/prompts primitives (tools cover the read plane)
  - elicitation/multi-round-trip flows
upstream:
  path: discover.md
  sha256: "7dae6c803714c3f327160815c3e5d47e6c041f404ee9aa85acac532225313b8b"
---

# intent

Read-plane engineering only — no transport changes, no breaking tool
renames, no provider calls.
