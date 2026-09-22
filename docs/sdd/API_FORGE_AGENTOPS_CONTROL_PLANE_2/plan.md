---
sdd: 1
feature: API_FORGE_AGENTOPS_CONTROL_PLANE_2
phase: plan
profile: standard
status: done
upstream:
  path: architecture.md
  sha256: "8cb7e37ca516ef766c741e7a6f31d217128b5a4bb052105b854a329b1d10eca7"
tasks:
  - id: control-contracts
    covers: [persisted-control-run, dynamic-ready-width]
    test: sdd/API_FORGE_AGENTOPS_CONTROL_PLANE_2/evidence/control-tests.txt
    risk: medium
    rollback: remove control.py and retain existing runtime
  - id: lifecycle
    covers: [retry-budget-cancel, replayable-events]
    test: sdd/API_FORGE_AGENTOPS_CONTROL_PLANE_2/evidence/control-tests.txt
    risk: medium
    rollback: disable control CLI
  - id: review-cli
    covers: [independent-review]
    test: sdd/API_FORGE_AGENTOPS_CONTROL_PLANE_2/evidence/control-tests.txt
    risk: low
    rollback: leave runs awaiting supervision
---

# plan

Implementar contratos, persistência append-only, lifecycle e CLI local. Não
alterar os adapters de modelo nem promover qualquer mutação externa.
