---
sdd: 1
feature: API_FORGE_RELATIONAL_RDS_SPECIALIZATION_1
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "bd9ab1c4413828609cd64880ea40871d88d5cea07d69d296f7b9168da01d1e5a"
problem: >
  APIs relacionais não tinham facts para SQL, pool, transação e paginação,
  nem um collector AWS para postura de instância e cluster RDS/Aurora.
success: [relational-source-ir, rds-posture-dump, no-live-query]
out_of_scope: [query-execution, explain-live, index-creation]
owner: api-forge-data-access
---
# intent

Adicionar a primeira camada de especialização relacional sem executar banco.
