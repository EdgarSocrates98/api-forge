---
sdd: 1
feature: API_FORGE_PERFORMANCE_CONTROL_PLANE_E
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "424d927e550b1a157601c3b85fcdeebd449b86440bbb684ea16d96f69ae00ac5"
covers: [PerformancePlan/v1, PerformanceAssessment/v1]
api_ir:
  input: endpoints, target_tps, thresholds and measured PerformanceRun
  output: PASS, FAIL or INCONCLUSIVE with evidence gaps
---
# contract

O plano mantém execução externa desabilitada; a avaliação não transforma ausência em zero.
