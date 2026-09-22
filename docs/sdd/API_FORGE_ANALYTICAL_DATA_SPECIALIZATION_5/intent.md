---
sdd: 1
feature: API_FORGE_ANALYTICAL_DATA_SPECIALIZATION_5
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "fb1472a64701672e54aa4eeb215fd72f56a13062ff6e33737990d51db06092cf"
problem: >
  Agentes não tinham uma IR para diferenciar busca, aggregation, paginação,
  partição e writes em engines analíticas.
success: [analytical-ir, search-safety, partition-signal]
out_of_scope: [query-plan-live, shard-rebalance, cluster-mutation]
owner: api-forge-analytics
---
# intent

Adicionar análise estática de OpenSearch/Elasticsearch e Redshift.
