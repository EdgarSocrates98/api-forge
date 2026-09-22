---
sdd: 1
feature: API_FORGE_OBSERVABILITY_CIRCUIT_CONTROL_PLANE_R
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "a38e86eb36d8a204104a3b043f8242be3e6aeb43955efdb733e128508d6922d6"
covers: [CircuitBreakerEvent/v1, CircuitBreakerMetrics/v1]
api_ir:
  input: provider circuit events
  output: provider metrics and alert identifiers
---
# contract

Eventos não carregam segredos; métricas são provider-scoped e alertas são identificadores estáveis.
