---
sdd: 1
feature: API_FORGE_ANALYTICAL_DATA_SPECIALIZATION_5
phase: discover
profile: standard
status: draft
approaches:
  - id: latency-promise
    summary: prometer performance de OpenSearch/Redshift pelo código
    verdict: refused -- requer cluster, workload e métricas reais
  - id: analytical-ir
    summary: extrair operações, paginação, agregação e partição observáveis
    verdict: chosen -- orienta investigação sem inventar capacidade
chosen: analytical-ir
---
# discover

O projeto ainda não possuía especialização de busca e analytics para OpenSearch/Redshift.
