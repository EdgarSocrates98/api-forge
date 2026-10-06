---
sdd: 1
feature: API_FORGE_FIELD_VALIDATION
phase: secure
profile: critical
status: draft
upstream:
  path: verify.md
  sha256: "bf4a1f53ade6c9e671e74d86e3c72e25a8027ec97990cfc29cc3f392197637f8"
threat_model: docs/security/threat-model-mvp.md
---
# secure

Offline only: no network, no provider SDK, no repository code executed. Own repositories appear only as `sha256:` refs; local names and paths live in the git-ignored `docs/field/repos.local.yaml`, and export refuses with `AF-FIELD-EXPORT-LEAK` before writing. `field verify` never echoes human labels.
