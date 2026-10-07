---
sdd: 1
feature: API_FORGE_OBSERVABILITY_OPERATIONAL_READINESS_D
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "7664ae84d27a8d4230cfff6be45e160eef797d7f54c8db8e14ffae77f33b9a8f"
covers: [ObservabilityExportReadiness/v1]
api_ir:
  input: HostExportBinding, CredentialStatus, allowlist and host sender metadata
  output: ready, review or blocked with named checks
---
# contract

O contrato registra apenas metadados e sempre marca `network_called: false`.
