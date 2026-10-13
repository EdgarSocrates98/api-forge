---
sdd: 1
feature: API_FORGE_OBSERVABILITY_CREDENTIAL_BROKER_J
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "d5e95280a92ddf8ade92b92069fecb69086df35a9b0af7270736ca92126c4cc6"
covers: [CredentialReference/v1, CredentialStatus/v1, ReadReceipt/v1]
api_ir:
  input: provider, reference metadata and read plan
  output: blocked, fixture_only or future executed receipt
---
# contract

Credential values are never returned by these contracts.
