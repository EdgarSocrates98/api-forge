---
sdd: 1
feature: API_FORGE_OBSERVABILITY_CIRCUIT_EXPORTERS_S
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "e4782f4c2072fdb22d0da8aaa53a6b6862e90ffd08062373f30b7acf7d4c25c3"
tasks:
  - id: optional-exporters
    status: done
    evidence: sdd/API_FORGE_OBSERVABILITY_CIRCUIT_EXPORTERS_S/evidence/exporter-tests.txt
claims: [provider-payloads, callback-only, no-secret-leak]
---
# build

Exportadores opcionais para OTel, Datadog e Dynatrace implementados.
