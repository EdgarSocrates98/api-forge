---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HEALTH_CORRELATION_F
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "2dbf65b1451aefc04f505a80d39c46c57a8bf035e9407a25fd03e501b1e0385e"
covers: [HealthAssessment/v1]
api_ir:
  input: TelemetryRecord, SLOResult and optional performance verdicts
  output: status, severity, signals, actions, gaps and evidence
---
# contract

HealthAssessment é provider-neutral, versionado e não executa remediação.
