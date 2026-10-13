---
sdd: 1
feature: API_FORGE_ECONOMY_EVALS
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "4814e65007afbb167e6b9180a4889d79c0e138b5bd0140e7eca524229e958712"
covers:
- EconomyMatrix/v1
- EvaluationGate/v1
- ReplayReport/v1
- RoleROI/v1
- InformationGain/v1
api_ir:
  input: canonical contract pairs, stored runs, two matrix reports
  output: matrix report, gate decision, replay report, role ROI, information gain
---
# contract

`ScorecardRoutingPolicy` gains optional `quality_floor` (default null, no behavior change); the runtime economy block gains `information_gain`.
