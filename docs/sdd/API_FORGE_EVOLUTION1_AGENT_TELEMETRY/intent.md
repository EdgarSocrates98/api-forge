---
sdd: 1
feature: API_FORGE_EVOLUTION1_AGENT_TELEMETRY
phase: intent
profile: critical
status: done
risk_class: high
problem: >
  Agentic execution has trajectory events but no closed OTel-shaped record for
  agent/tool spans with sensitive-attribute refusal and bounded local query.
success:
  - agent-tool-span-contract
  - sensitive-attribute-gate
  - append-only-telemetry
  - cli-mcp-parity
  - documentation-and-evidence
out_of_scope:
  - exporter/network calls
  - credentials or secret values
  - production performance claims
upstream:
  path: discover.md
  sha256: "2ff21a6a7a350099105975df972701027afe6bc3038b600c2997370df0ca2cc9"
---

# intent

Make local agent/tool execution observable as evidence without turning
telemetry payloads into instructions or enabling network export.
