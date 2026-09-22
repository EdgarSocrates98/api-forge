---
sdd: 1
feature: API_FORGE_RELATIONAL_RDS_SPECIALIZATION_1
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "a3215bd3d15f06926a64eb5ef20991853176a57e7d5d3d82326cf4946299f349"
files: [src/apiforge/adapters/relational.py, src/apiforge/collectors/datastores.py, src/apiforge/cli.py]
decisions:
  - id: source-only
    decision: usar scanner textual e facts com proveniência
    rollback: remover o adapter relacional
  - id: dump-boundary
    decision: collector só escreve dump de describe_db_instances e describe_db_clusters
    rollback: manter somente análise local
---
# architecture

PostgreSQL, MySQL/MariaDB e Aurora são tratados como engines relacionais declaradas; RDS é o boundary AWS.
