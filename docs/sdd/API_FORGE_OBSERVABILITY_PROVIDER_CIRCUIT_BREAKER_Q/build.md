---
sdd: 1
feature: API_FORGE_OBSERVABILITY_PROVIDER_CIRCUIT_BREAKER_Q
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "5d94c0c5cf5136094f3eac60dffe5b2463ccf4e2b686206e246da07e05e66d54"
tasks:
  - id: provider-breaker
    status: done
    evidence: sdd/API_FORGE_OBSERVABILITY_PROVIDER_CIRCUIT_BREAKER_Q/evidence/circuit-tests.txt
claims: [fail-fast, half-open-probe, receipt-evidence]
---
# build

Circuit breaker por transport implementado com política configurável.
