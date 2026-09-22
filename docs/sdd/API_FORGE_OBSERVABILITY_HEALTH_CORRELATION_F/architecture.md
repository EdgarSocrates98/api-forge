---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HEALTH_CORRELATION_F
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "123c7ea371e71fff96e1964e0a5521b4a77edcf00dc8b43362c0ee6cc523f5fc"
files: [src/apiforge/observability/health.py, src/apiforge/cli.py]
decisions:
  - id: explicit-gaps
    decision: ausência de telemetria produz inconclusive
    rollback: remover correlator e manter ingestão existente
---
# architecture

O correlator compõe summaries e SLOResults existentes; adapters Datadog, Dynatrace e AWS permanecem limites de projeção.
