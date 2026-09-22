---
sdd: 1
feature: API_FORGE_OBSERVABILITY_AUTHENTICATED_READ_ADAPTERS_K
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "51cbabb901b767e80e6b0131c692909b9f42b624765a8d73daf396d496fb2ac7"
covers: [ReadTransport/v1, ReadReceipt/v1]
api_ir:
  input: ReadPlan, available CredentialStatus and injected GET transport
  output: executed or blocked receipt, never mutation
---
# contract

O receipt informa contagem, rede e mutação; valores de credenciais nunca aparecem.
