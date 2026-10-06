---
sdd: 1
feature: API_FORGE_OBSERVABILITY_PROVIDER_QUERY_BUILDERS_M
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "4645afb15f83fdde9e1ae866d4ae98921cf64133af72c33744d12b3f339afc3d"
tasks:
  - id: provider-query-builders
    status: done
    evidence: sdd/API_FORGE_OBSERVABILITY_PROVIDER_QUERY_BUILDERS_M/evidence/query-tests.txt
claims: [provider-specific, pure, credential-free]
---
# build

Implementados os encoders de Datadog, Dynatrace, CloudWatch e OTel.
