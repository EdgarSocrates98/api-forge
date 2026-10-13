---
sdd: 1
feature: API_FORGE_OBSERVABILITY_REQUEST_RESILIENCE_O
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "bc07b6efe2e8f37659220e8da1031e41b070ff9ad8c1dd4aa836e9eec65c08e4"
covers: [ReadRetryPolicy/v1, request_attempts]
api_ir:
  input: ProviderRequester and ReadRetryPolicy
  output: bounded provider response or propagated terminal error
---
# contract

`ReadRetryPolicy` define tentativas, backoff inicial e teto; o receipt registra a quantidade de tentativas.
