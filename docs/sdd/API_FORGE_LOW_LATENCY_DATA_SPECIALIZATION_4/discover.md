---
sdd: 1
feature: API_FORGE_LOW_LATENCY_DATA_SPECIALIZATION_4
phase: discover
profile: standard
status: draft
approaches:
  - id: generic-database-advice
    summary: aplicar a mesma recomendação a Redis e DynamoDB
    verdict: refused -- modelos de latência e particionamento são diferentes
  - id: observed-profile
    summary: derivar riscos somente dos facts de cada adapter
    verdict: chosen -- sem inferência de índice ou capacidade
chosen: observed-profile
---
# discover

Redis e DynamoDB já tinham scanners, mas faltava um perfil explícito de baixa latência e escala particionada.
