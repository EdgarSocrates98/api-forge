---
sdd: 1
feature: API_FORGE_HOST_ACTIVATION_PLAN_I
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "2f4faa493096a4dcb404cf55c701c838dcc04310196f603a601017fbced45257"
tasks:
  - id: activation-contract
    covers: [activation-plan, host-limitations]
    test: sdd/API_FORGE_HOST_ACTIVATION_PLAN_I/evidence/activation-tests.txt
    risk: low
    rollback: remove activation.py
  - id: cli
    covers: [approval-gate]
    test: sdd/API_FORGE_HOST_ACTIVATION_PLAN_I/evidence/activation-tests.txt
    risk: medium
    rollback: remove activation-plan command
---
# plan

Adicionar plano por host, CLI e testes de recusa.
