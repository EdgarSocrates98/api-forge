---
sdd: 1
feature: API_FORGE_ECONOMY_EVAL_INTEGRITY
phase: secure
profile: critical
status: draft
upstream:
  path: verify.md
  sha256: "5947ed5ae30f68203886bbaf0229966a73626ab3d090892115175168c2f3a34a"
threat_model: docs/security/threat-model-mvp.md
---
# secure

Caller-supplied paths (`--changed`, `--case-dir`, `--case`) now obey the same allowed-roots resolver as case data; one threat-model row added in EN and PT-BR.
