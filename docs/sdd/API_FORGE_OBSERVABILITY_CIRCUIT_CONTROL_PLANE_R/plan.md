---
sdd: 1
feature: API_FORGE_OBSERVABILITY_CIRCUIT_CONTROL_PLANE_R
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "8ed6da297a43d4857634094af83b2180efe75b3f075c2225c841acc90bee5e10"
tasks:
  - id: events
    covers: [provider-events]
    test: sdd/API_FORGE_OBSERVABILITY_CIRCUIT_CONTROL_PLANE_R/evidence/control-plane-tests.txt
    risk: high
    rollback: remover event_sink do transport
  - id: projection
    covers: [provider-metrics, deterministic-alerts]
    test: sdd/API_FORGE_OBSERVABILITY_CIRCUIT_CONTROL_PLANE_R/evidence/control-plane-tests.txt
    risk: medium
    rollback: remover metrics_for_provider
---
# plan

Adicionar contratos, sink em memória e projeção de métricas/alertas por provider.
