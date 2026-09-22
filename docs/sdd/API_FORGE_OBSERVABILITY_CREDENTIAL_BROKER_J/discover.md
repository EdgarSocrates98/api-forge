---
sdd: 1
feature: API_FORGE_OBSERVABILITY_CREDENTIAL_BROKER_J
phase: discover
profile: standard
status: draft
approaches:
  - id: core-secret
    summary: ler tokens diretamente no núcleo
    verdict: refused -- viola isolamento e auditabilidade
  - id: broker-gate
    summary: referência metadata-only e broker externo
    verdict: chosen -- bloqueia sem autorização
chosen: broker-gate
---
# discover

Os planos read-only precisam de uma fronteira de credenciais antes de conectores reais.
