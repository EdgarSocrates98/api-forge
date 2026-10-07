---
sdd: 1
feature: API_FORGE_OBSERVABILITY_PROVIDER_CIRCUIT_BREAKER_Q
phase: benchmark
profile: standard
status: draft
upstream:
  path: secure.md
  sha256: "b7b1d5d46415bdeac3105b06d4a7e1f370c1c37865100384bc65e3a8bafeb400"
baseline: retry bounded without fail-fast state
results:
  - artifact: sdd/API_FORGE_OBSERVABILITY_PROVIDER_CIRCUIT_BREAKER_Q/evidence/circuit-tests.txt
    outcome: measured-by-test
    note: janela real depende de relógio e ambiente de provider aprovado
---
# benchmark

Chamadas em `open` têm custo de rede zero; tempos de recuperação são controlados por política.
