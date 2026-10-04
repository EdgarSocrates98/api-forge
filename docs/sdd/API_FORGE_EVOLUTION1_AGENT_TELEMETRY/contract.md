---
sdd: 1
feature: API_FORGE_EVOLUTION1_AGENT_TELEMETRY
phase: contract
profile: critical
status: done
upstream:
  path: intent.md
  sha256: "4a24723e96d857f83a89ab132c5a1ef248cde9ab83b2a169ef9ad0cb0cac9a21"
covers:
  - agent-tool-span-contract
  - sensitive-attribute-gate
  - append-only-telemetry
  - cli-mcp-parity
  - documentation-and-evidence
---

# contract

Add `AgentSpan/v1` with trace/span identity, operation kind, agent/tool
attributes, status, timestamps, evidence and bounded attributes. Sensitive
attribute names are refused; values are never redacted after persistence.
