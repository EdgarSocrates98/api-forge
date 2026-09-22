---
sdd: 1
feature: API_FORGE_PERFORMANCE_CAPACITY_VALIDATION_C
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "fd1c51ab0b06ac4fc24ef9db79d50be2dd492e7ad44cf258904f9b9995b58834"
covers: [CapacityAssessment/v1]
api_ir:
  input: PerformanceRun/v1 and declared headroom policy
  output: passed, failed or inconclusive capacity assessment
---
# contract

`CapacityAssessment/v1` referencia o run de origem, lista evidências e bloqueios e só emite `max_safe_tps` quando o run passou.
