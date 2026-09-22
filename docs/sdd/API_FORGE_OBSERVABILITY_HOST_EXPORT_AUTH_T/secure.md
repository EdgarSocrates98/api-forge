---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HOST_EXPORT_AUTH_T
phase: secure
profile: standard
status: draft
upstream:
  path: verify.md
  sha256: "517b2072754c41072048015f9c1b8b52aae530f349ea6c7ff0b94f7953ae9155"
threat_model: docs/security/threat-model-mvp.md
---
# secure

O core só manipula referência opaca; resolução de secret, headers, TLS, timeout e retry são responsabilidades do host.
