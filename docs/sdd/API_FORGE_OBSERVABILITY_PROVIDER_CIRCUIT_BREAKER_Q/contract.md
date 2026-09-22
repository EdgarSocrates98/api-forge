---
sdd: 1
feature: API_FORGE_OBSERVABILITY_PROVIDER_CIRCUIT_BREAKER_Q
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "3c1c4455efd48cab7463b1ef604b990a3da0f41ddf9a35d9c802e540c0e97f29"
covers: [CircuitBreakerPolicy/v1, circuit_state, circuit_violations]
api_ir:
  input: transient provider failures and recovery clock
  output: executed, transient-blocked or circuit-open receipt
---
# contract

O estado do circuito e a decisão de rede são observáveis; `open` bloqueia antes do requester.
