---
sdd: 1
feature: API_FORGE_PERFORMANCE_CONTROL_PLANE_E
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "dc9f15b85fe5662bdd220bd215ee81515a852b8beb6f9c263d2693472cfa1f25"
files: [src/apiforge/perf_control/models.py, src/apiforge/perf_control/service.py, src/apiforge/cli.py]
decisions:
  - id: no-execution
    decision: gerar plano, não executar ferramenta
    rollback: remover comando perf plan
---
# architecture

O control plane compõe sobre PerformanceRun e deixa execução a cargo de um adapter aprovado.
