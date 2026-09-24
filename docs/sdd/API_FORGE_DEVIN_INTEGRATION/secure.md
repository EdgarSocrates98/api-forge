---
sdd: 1
feature: API_FORGE_DEVIN_INTEGRATION
phase: secure
profile: standard
status: draft
upstream:
  path: verify.md
  sha256: "c5025a1c5b75065f7c06756d3eb298ece1339a161e1ef4e68d2835232df3d2e3"
threat_model: docs/security/threat-model-mvp.md
---
# secure

The Devin hook blocks irreversible Git/Docker cleanup patterns. Project config
asks before commit, push, Docker and secret-file writes. The core remains
provider- and credential-free.
