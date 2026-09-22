---
sdd: 1
feature: API_FORGE_OBSERVABILITY_PROVIDER_CIRCUIT_BREAKER_Q
phase: secure
profile: standard
status: draft
upstream:
  path: verify.md
  sha256: "af560f1594f78bd59646904ced5211957765eba489fee1deac5dd9ea19eee351"
threat_model: docs/security/threat-model-mvp.md
---
# secure

O estado `open` impede chamadas adicionais durante falha sustentada e registra explicitamente a ausência de rede.
