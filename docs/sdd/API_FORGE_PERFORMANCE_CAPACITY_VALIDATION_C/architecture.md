---
sdd: 1
feature: API_FORGE_PERFORMANCE_CAPACITY_VALIDATION_C
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "3ad34dd8bf7cca7092995e5f3f130bf243f74d15686b1aaf3306b66665cab71d"
files: [src/apiforge/contracts/stubs.py, src/apiforge/perf/capacity.py, src/apiforge/contracts/registry.py]
decisions:
  - id: compose-existing-verdict
    decision: reutilizar o veredito de PerformanceRun como fonte única de semântica
    rollback: remover assess_capacity e manter apenas perf verdict
  - id: no-network
    decision: avaliação local e determinística, sem executar carga ou tocar infraestrutura
    rollback: desabilitar o comando até existir adapter aprovado
---
# architecture

O módulo de capacidade é uma composição read-only sobre medições existentes.
