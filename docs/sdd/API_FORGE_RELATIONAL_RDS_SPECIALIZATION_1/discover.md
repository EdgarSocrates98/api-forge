---
sdd: 1
feature: API_FORGE_RELATIONAL_RDS_SPECIALIZATION_1
phase: discover
profile: standard
status: draft
approaches:
  - id: live-db-probe
    summary: conectar em RDS e executar queries para descobrir comportamento
    verdict: refused -- exige credenciais e impacto externo
  - id: source-and-dump
    summary: extrair access patterns e postura RDS para dumps offline
    verdict: chosen -- seguro e reproduzível
chosen: source-and-dump
---
# discover

O API Forge tinha collectors de DynamoDB, DocDB e Neptune, mas não uma especialização relacional completa para RDS/Aurora.
