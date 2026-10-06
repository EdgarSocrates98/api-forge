---
sdd: 1
feature: API_FORGE_OBSERVABILITY_READ_SAFETY_POLICY_L
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "f9fc0c2cc72fb9c9a02c7ef1c795e4302bd324d00243aa339199cc1475eb9efb"
covers: [ReadSafetyPolicy/v1, ReadReceipt/v1]
api_ir:
  input: normalized provider response and safety policy
  output: executed receipt or blocked receipt with violations
---
# contract

`ReadSafetyPolicy` limita `max_records` e `max_response_bytes`. O receipt bloqueado preserva a evidência de rede sem expor o payload.
