---
sdd: 1
feature: API_FORGE_OBSERVABILITY_PROVIDER_CIRCUIT_BREAKER_Q
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "91936b7b1adac66a40168e8b9dd05c6937ee03f6094a8eff9ecd0032b1bdd8df"
tasks:
  - id: state-machine
    covers: [closed-open-half-open, recovery-window]
    test: sdd/API_FORGE_OBSERVABILITY_PROVIDER_CIRCUIT_BREAKER_Q/evidence/circuit-tests.txt
    risk: high
    rollback: remover circuit_breaker.py
  - id: receipts
    covers: [circuit-evidence]
    test: sdd/API_FORGE_OBSERVABILITY_PROVIDER_CIRCUIT_BREAKER_Q/evidence/circuit-tests.txt
    risk: medium
    rollback: bloquear toda leitura externa
---
# plan

Implementar máquina de estados, janela de recuperação, clock injetável e receipts de bloqueio.
