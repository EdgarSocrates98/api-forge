---
sdd: 1
feature: API_FORGE_ECONOMY_EVALS
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "9c4b12669d71ba450814a87306dedb413f69809d653333cc5c9957ca40d70f08"
tasks:
- id: contracts
  status: done
  evidence: sdd/API_FORGE_ECONOMY_EVALS/evidence/economy-evals-tests.txt
- id: matrix
  status: done
  evidence: sdd/API_FORGE_ECONOMY_EVALS/evidence/economy-matrix.json
- id: gate-replay
  status: done
  evidence: sdd/API_FORGE_ECONOMY_EVALS/evidence/economy-evals-tests.txt
- id: roi-gain
  status: done
  evidence: sdd/API_FORGE_ECONOMY_EVALS/evidence/economy-evals-tests.txt
- id: quality-floor
  status: done
  evidence: sdd/API_FORGE_ECONOMY_EVALS/evidence/economy-evals-tests.txt
claims:
- economy-matrix
- holdout-mutation
- evaluation-gate
- replay
- role-roi
- information-gain
- quality-floor
---
# build

Implemented `evals economy-matrix|gate|replay`, `economy roi`, `economy.information_gain` and the opt-in quality floor; MCP parity for gate, replay and ROI.
