---
sdd: 1
feature: API_FORGE_PERFORMANCE_CAPACITY_VALIDATION_C
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "1c864c2d8c78fd0b8e9ee1e31b29b9586431de0df8daffb683ac2124cf15bd3e"
problem: >
  Sem um envelope formal, consumidores podem reutilizar um TPS observado como
  promessa de produção, mesmo com falhas, saturação ou evidência incompleta.
success: [capacity-assessment, safe-tps-envelope, inconclusive-on-missing-evidence]
out_of_scope: [executar-carga, provisionar-infraestrutura, inventar-métricas]
owner: api-forge-performance
---
# intent

Publicar capacidade medida como contrato versionado e acionável.
