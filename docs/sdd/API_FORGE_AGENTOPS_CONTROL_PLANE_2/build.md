---
sdd: 1
feature: API_FORGE_AGENTOPS_CONTROL_PLANE_2
phase: build
profile: standard
status: done
upstream:
  path: plan.md
  sha256: "9c85a151a8e7b8d024f11ffac31c731e3b9657241f007c76509d002512937236"
tasks:
  - id: control-contracts
    status: done
    evidence: sdd/API_FORGE_AGENTOPS_CONTROL_PLANE_2/evidence/control-tests.txt
  - id: lifecycle
    status: done
    evidence: sdd/API_FORGE_AGENTOPS_CONTROL_PLANE_2/evidence/control-tests.txt
  - id: review-cli
    status: done
    evidence: sdd/API_FORGE_AGENTOPS_CONTROL_PLANE_2/evidence/control-tests.txt
claims:
  - ControlPlane persists immutable run state and normalized events
  - ready steps expose dynamic parallel width without executing work
  - terminal runs refuse further execution
---

# build

Control Plane implementado em `apiforge.runtime.control` e exposto por
`runtime control-*`.
