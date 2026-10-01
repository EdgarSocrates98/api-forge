---
sdd: 1
feature: API_FORGE_LOW_LATENCY_DATA_SPECIALIZATION_4
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "06f6b6fd2e3d4cbe3d91b4273901c10704c9e7ab90e778de4dd3e268953ce398"
problem: >
  O agente não distinguia risco de TTL ausente em Redis de full scan e query
  sem chave em DynamoDB, nem classificava o perfil de latência.
success: [data-performance-profile, redis-ttl-risk, dynamo-access-risk]
out_of_scope: [hot-key-proof, index-recommendation, live-capacity]
owner: api-forge-data-access
---
# intent

Adicionar perfil de performance governado por fatos observados.
