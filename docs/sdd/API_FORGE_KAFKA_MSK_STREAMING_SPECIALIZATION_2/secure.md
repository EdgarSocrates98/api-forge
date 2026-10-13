---
sdd: 1
feature: API_FORGE_KAFKA_MSK_STREAMING_SPECIALIZATION_2
phase: secure
profile: standard
status: draft
upstream:
  path: verify.md
  sha256: "aff17f9d9b79cc5c27f16fe416ce4f798c79b62aa0146227362804a4c3a31ed9"
threat_model: docs/security/threat-model-mvp.md
---
# secure

Nenhum consumer é iniciado; o modelo não cria tópico, publica mensagem ou comita offset.
