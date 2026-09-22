---
sdd: 1
feature: API_FORGE_OBSERVABILITY_CIRCUIT_CONTROL_PLANE_R
phase: discover
profile: standard
status: draft
approaches:
  - id: provider-blind
    summary: manter o breaker sem eventos nem métricas
    verdict: refused -- dificulta operação e diagnóstico
  - id: event-sink-projection
    summary: emitir eventos e projetar métricas/alertas por provider
    verdict: chosen -- observável e desacoplado de vendors
chosen: event-sink-projection
---
# discover

O circuit breaker protegia a rede, mas ainda não alimentava o control plane com sinais operacionais.
