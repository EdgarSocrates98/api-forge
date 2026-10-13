---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HEALTH_CORRELATION_F
phase: intent
profile: standard
status: draft
upstream:
  path: discover.md
  sha256: "43c63021595111e623e9699ed52591ecdd7e339b7202f7ad7a6dce3d915958c2"
problem: >
  Um agent precisa distinguir serviço saudável, degradado, incidente e ausência
  de observabilidade sem depender de Datadog ou Dynatrace.
success: [health-assessment, incident-correlation, explicit-observability-gaps]
out_of_scope: [external-alert-mutation, provider-credentials, auto-remediation]
owner: api-forge-observability
---
# intent

Correlacionar sinais com ações operacionais recomendadas e evidências.
