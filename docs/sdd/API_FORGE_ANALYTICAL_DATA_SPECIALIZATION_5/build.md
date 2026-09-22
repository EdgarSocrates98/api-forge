---
sdd: 1
feature: API_FORGE_ANALYTICAL_DATA_SPECIALIZATION_5
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "ee84c4ef3ea2e30133d9eed9463db107262218d5bfa1c75636485bcc3cdf289e"
tasks:
  - id: analytical-access
    status: done
    evidence: sdd/API_FORGE_ANALYTICAL_DATA_SPECIALIZATION_5/evidence/analytical-tests.txt
claims: [opensearch-search, redshift-aggregation, partition-signal]
---
# build

Implementado `AnalyticalAccessIR/v1`, `model opensearch-access` e `model redshift-access`.
