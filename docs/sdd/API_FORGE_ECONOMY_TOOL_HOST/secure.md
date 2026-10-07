---
sdd: 1
feature: API_FORGE_ECONOMY_TOOL_HOST
phase: secure
profile: standard
status: draft
upstream:
  path: verify.md
  sha256: "ba49de673819ba90999062f345b698a88985fb002da1afd775550a9d90fe5dfc"
threat_model: docs/security/threat-model-mvp.md
---
# secure

JUnit XML with a DOCTYPE is refused before parsing, so no entity (internal or external) is ever expanded; inputs are capped at 25 MB. `apiforge_call` dispatches only to registered tool functions — no dynamic import, no shell. Compact output and gateway results remove only null and empty values.
