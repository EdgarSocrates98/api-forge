---
sdd: 1
feature: API_FORGE_DEVIN_INTEGRATION
phase: discover
profile: standard
status: draft
approaches:
  - id: direct-sdk
    summary: call Devin APIs from the API Forge core
    verdict: refused -- violates offline-first and mutation boundaries
  - id: payload-first
    summary: generate governed payloads and native Devin configuration
    verdict: chosen -- local, auditable and surface-specific
chosen: payload-first
---
# discover

Official Devin Desktop/CLI docs were reviewed for configuration, commands,
permissions, MCP, skills, subagents, hooks and Cloud handoff.
