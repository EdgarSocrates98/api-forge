---
sdd: 1
feature: API_FORGE_DATA_ACCESS_GOVERNED_ADAPTERS_E
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "02a83b602d6e565cacbae39a4037b151b417f7ecce1e011696bd83bb2482f5b8"
problem: >
  Um agente pode tratar descoberta estática como autorização para operar um
  datastore, ou perder que uma operação extraída é mutável.
success: [database-readiness, mutation-gate, no-live-connection]
out_of_scope: [credenciais-reais, consultas-live, writes-em-bancos]
owner: api-forge-data-access
---
# intent

Tornar explícita a fronteira entre inventário, prontidão e execução externa.
