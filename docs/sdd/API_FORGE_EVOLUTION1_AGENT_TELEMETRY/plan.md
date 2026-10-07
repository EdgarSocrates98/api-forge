---
sdd: 1
feature: API_FORGE_EVOLUTION1_AGENT_TELEMETRY
phase: plan
profile: critical
status: ready
upstream:
  path: architecture.md
  sha256: "cf1609af968afce3116a21af0dd092698f200878e7520968c13c82ba547b3fe4"
tasks:
  - id: T1
    covers: [agent-tool-span-contract, sensitive-attribute-gate]
    test: sdd/API_FORGE_EVOLUTION1_AGENT_TELEMETRY/evidence/T1.txt
  - id: T2
    covers: [append-only-telemetry, cli-mcp-parity]
    test: sdd/API_FORGE_EVOLUTION1_AGENT_TELEMETRY/evidence/T2.txt
  - id: T3
    covers: [documentation-and-evidence]
    proof: sdd/API_FORGE_EVOLUTION1_AGENT_TELEMETRY/evidence/T3.txt
---

# plan

Build the closed span contract and pure local store, expose identical CLI/MCP
projections, then verify sensitive-key refusal, trace/task filtering and
append-only digests.
