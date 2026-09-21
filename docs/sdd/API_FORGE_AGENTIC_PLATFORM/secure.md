---
sdd: 1
feature: API_FORGE_AGENTIC_PLATFORM
phase: secure
profile: critical
status: draft
upstream:
  path: verify.md
  sha256: "f9ff9bf671f96dab33729dde882f6d11938ce224d61c446053aae07ac1d3c3ad"
threat_model: docs/security/threat-model-mvp.md
---

# secure

New surfaces to model: task seal forgery, scope widening by executors,
graph poisoning via untrusted facts, cache poisoning, DONE-refusal bypass.
