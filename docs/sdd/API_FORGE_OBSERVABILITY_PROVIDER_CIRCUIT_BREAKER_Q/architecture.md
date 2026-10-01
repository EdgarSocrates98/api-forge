---
sdd: 1
feature: API_FORGE_OBSERVABILITY_PROVIDER_CIRCUIT_BREAKER_Q
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "329863495a7bdac2ac80fa44ec30db3193d53f90157760a75082a244191a31f4"
files: [src/apiforge/contracts/observability.py, src/apiforge/observability/circuit_breaker.py, src/apiforge/observability/provider_transport.py, src/apiforge/observability/read_adapter.py]
decisions:
  - id: per-transport-state
    decision: manter estado no transport do provider
    rationale: isolamento e lifecycle explícito
    rollback: desabilitar circuit com threshold alto
  - id: injected-clock
    decision: injetar clock monotônico
    rationale: testes de janela sem espera real
    rollback: permitir apenas closed
---
# architecture

O breaker envolve a leitura paginada; falhas transitórias contam, respostas válidas fecham o circuito.
