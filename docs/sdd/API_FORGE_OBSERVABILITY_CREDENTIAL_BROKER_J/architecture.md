---
sdd: 1
feature: API_FORGE_OBSERVABILITY_CREDENTIAL_BROKER_J
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "94bd243ad6147fc4b6eda7e22e526df6f601f4823bd4ae634b6ab24759f88eba"
files: [src/apiforge/observability/credentials.py, src/apiforge/contracts/observability.py]
decisions:
  - id: blocked-default
    decision: broker ausente bloqueia leitura
    rollback: manter apenas fixture adapter
---
# architecture

O adapter futuro recebe um broker fora do core e devolve apenas receipt sanitizado.
