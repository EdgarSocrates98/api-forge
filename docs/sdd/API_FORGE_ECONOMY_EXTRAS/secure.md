---
sdd: 1
feature: API_FORGE_ECONOMY_EXTRAS
phase: secure
profile: standard
status: draft
upstream:
  path: verify.md
  sha256: "e9ef7b5580512f10202e041c37843d400d7b53e633f2fce4cefa9cfa3f256ce3"
threat_model: docs/security/threat-model-mvp.md
---
# secure

All verbs are read-only; `verify plan` prints commands but never runs them. Evidence slices and retrieved passages are stored in the local ctx CAS only. Tiering never downgrades without recorded benchmark evidence.
