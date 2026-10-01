---
sdd: 1
feature: API_FORGE_RELATIONAL_RDS_SPECIALIZATION_1
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "e5e285e513bb019b46b972341013ba8dc1d23fa2b49de4b969322ab42d06ae59"
tasks:
  - id: relational-rds
    status: done
    evidence: sdd/API_FORGE_RELATIONAL_RDS_SPECIALIZATION_1/evidence/rds-tests.txt
claims: [postgres-mysql-scanner, rds-collector, no-live-query]
---
# build

Implementado scanner relacional, comandos `model rds-access`, `model postgres-access`, `model mysql-access` e `collect rds`.
