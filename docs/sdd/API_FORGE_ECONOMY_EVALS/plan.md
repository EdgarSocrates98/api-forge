---
sdd: 1
feature: API_FORGE_ECONOMY_EVALS
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "3f25adea3b154ac1ca12d8a62ca40c54fd46acb4a28f5ac5b6258e5c41aedc46"
tasks:
- id: contracts
  covers:
  - EconomyMatrix/v1
  - EvaluationGate/v1
  - ReplayReport/v1
  - RoleROI/v1
  - InformationGain/v1
  test: sdd/API_FORGE_ECONOMY_EVALS/evidence/economy-evals-tests.txt
  risk: low
  rollback: remove contracts/economy_evals.py
- id: matrix
  covers:
  - economy-matrix
  - holdout-mutation
  test: sdd/API_FORGE_ECONOMY_EVALS/evidence/economy-matrix.json
  risk: low
  rollback: remove evals/matrix.py and the corpus
- id: gate-replay
  covers:
  - evaluation-gate
  - replay
  test: sdd/API_FORGE_ECONOMY_EVALS/evidence/economy-evals-tests.txt
  risk: low
  rollback: remove evals/gate.py and evals/replay.py
- id: roi-gain
  covers:
  - role-roi
  - information-gain
  test: sdd/API_FORGE_ECONOMY_EVALS/evidence/economy-evals-tests.txt
  risk: low
  rollback: remove economy/roi.py and runtime/information_gain.py
- id: quality-floor
  covers:
  - quality-floor
  test: sdd/API_FORGE_ECONOMY_EVALS/evidence/economy-evals-tests.txt
  risk: medium
  rollback: unset quality_floor
---
# plan

Contracts, matrix and corpus, gate, replay and corpus, ROI, information gain, quality floor, surfaces.
