---
sdd: 1
feature: API_FORGE_OBSERVABILITY_READ_ADAPTERS_G
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "2e2443522e6394133fae2c4153033d15ac69d6c6175d2db24aabef2f934b6e06"
files: [src/apiforge/observability/read.py, src/apiforge/contracts/observability.py]
decisions:
  - id: fixture-first
    decision: planos começam em fixture_only e network_allowed=false
    rollback: remover read-plan mantendo ingestão OTel local
---
# architecture

O broker de credenciais e a execução real serão adapters posteriores, nunca responsabilidade do contrato.
