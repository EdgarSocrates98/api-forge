---
sdd: 1
feature: API_FORGE_EVOLUTION1_AGENT_TELEMETRY
phase: architecture
profile: critical
status: done
upstream:
  path: contract.md
  sha256: "4c2900a11e256f845976afc4eaf84ca9bfa725733511c2c309f4b6f14c260cac"
files:
  - src/apiforge/contracts/agent_telemetry.py
  - src/apiforge/runtime/agent_telemetry.py
  - src/apiforge/cli_agentic_state.py
  - src/apiforge/mcp/tools.py
decisions:
  - id: local-evidence
    summary: append spans to local JSONL and query by trace/task
    rollback: remove telemetry projections without changing runtime outcomes
  - id: deny-sensitive-keys
    summary: reject secret-like attribute names at contract validation
    rollback: preserve event identity while requiring sanitized attributes
  - id: otel-shaped
    summary: align names with agent/tool semantic conventions without exporter dependency
    rollback: retain versioned local schema and its explicit evidence boundary
---

# architecture

The service is provider-free and sits below CLI/MCP. It shares the same
append-only and canonical JSON projection rules as memory and budget state.
