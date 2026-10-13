---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HOST_HTTP_REQUESTER_N
phase: secure
profile: standard
status: draft
upstream:
  path: verify.md
  sha256: "bdc5fc612b54e42f3a4b93d1eb33c3bd7e67655b3dcb287af8aac348647b1a23"
threat_model: docs/security/threat-model-mvp.md
---
# secure

A allowlist reduz SSRF; o núcleo nunca resolve credenciais nem constrói headers de autenticação.
