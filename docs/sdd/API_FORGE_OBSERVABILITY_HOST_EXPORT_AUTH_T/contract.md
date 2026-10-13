---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HOST_EXPORT_AUTH_T
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "f32a5a507f7c0d1530aa5784fd7c5f46ff539f3bb96adbed6dc060f7fa8458f2"
covers: [HostExportBinding/v1, CircuitMetricsExportReceipt/v1]
api_ir:
  input: metrics, approved host binding and CredentialStatus
  output: blocked or sent/failed export receipt
---
# contract

Receipt preserva referência opaca, approval id, status de rede e motivo sem serializar tokens.
