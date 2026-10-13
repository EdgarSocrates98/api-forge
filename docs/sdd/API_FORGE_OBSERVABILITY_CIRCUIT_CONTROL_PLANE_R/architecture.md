---
sdd: 1
feature: API_FORGE_OBSERVABILITY_CIRCUIT_CONTROL_PLANE_R
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "d0e4cd5a35be1adad9725beb761e221ffa43bea217cd3aa4aafe89b362f8681d"
files: [src/apiforge/contracts/observability.py, src/apiforge/observability/circuit_observability.py, src/apiforge/observability/circuit_breaker.py, src/apiforge/observability/provider_transport.py]
decisions:
  - id: injectable-sink
    decision: usar sink injetável com implementação em memória
    rationale: host pode exportar depois sem acoplar vendors ao core
    rollback: desabilitar emissão de eventos
  - id: deterministic-projection
    decision: projetar alertas a partir dos eventos observados
    rationale: comportamento reproduzível em CI e holdouts
    rollback: manter somente contadores locais
---
# architecture

O breaker emite eventos; o control plane agrega sem executar escrita externa.
