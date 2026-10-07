---
sdd: 1
feature: API_FORGE_HOST_ACTIVATION_PLAN_I
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "60b48a013514224bfb30f1f51bb67ccb605ea95607383867fd2add5b650f3a02"
tasks:
  - id: activation
    status: done
    evidence: sdd/API_FORGE_HOST_ACTIVATION_PLAN_I/evidence/activation-tests.txt
claims: [four-host-plans, no-silent-mutation]
---
# build

Implementado `ActivationPlan` e `agentops activation-plan`.
