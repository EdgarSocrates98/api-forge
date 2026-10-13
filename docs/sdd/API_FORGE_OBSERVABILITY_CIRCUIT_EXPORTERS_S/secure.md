---
sdd: 1
feature: API_FORGE_OBSERVABILITY_CIRCUIT_EXPORTERS_S
phase: secure
profile: standard
status: draft
upstream:
  path: verify.md
  sha256: "30a34d12ecb2bf191e51ed0962b559429bd7053d5ea4be85134ac46ec1028cee"
threat_model: docs/security/threat-model-mvp.md
---
# secure

O exporter não resolve credenciais, não cria headers e não serializa secrets nos receipts de erro.
