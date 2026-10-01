---
sdd: 1
feature: API_FORGE_RELATIONAL_RDS_SPECIALIZATION_1
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "cd14eebffc1dd454d651c0612caad2d6d643b795fa0ad85327aa23239e5c1fe0"
results:
  - gate: pytest relational and RDS collector tests
    outcome: pass
    evidence: 4 passed
  - gate: ruff, mypy and release gate
    outcome: pass
    evidence: evidence/rds-tests.txt
---
# verify

SQL, pool, paginação e transação são facts; nenhum query é executado.
