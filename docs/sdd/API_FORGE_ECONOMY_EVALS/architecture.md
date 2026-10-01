---
sdd: 1
feature: API_FORGE_ECONOMY_EVALS
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "077688ef0e674f2b8a83dbfcf9da56f90b2f8501ef67ab2d2e400f59ac722386"
files:
- src/apiforge/contracts/economy_evals.py
- src/apiforge/evals/matrix.py
- src/apiforge/evals/gate.py
- src/apiforge/evals/replay.py
- src/apiforge/economy/roi.py
- src/apiforge/runtime/information_gain.py
- src/apiforge/runtime/scorecard_routing.py
- src/apiforge/contracts/scorecard_routing.py
- src/apiforge/rules/agent_profiles.yaml
decisions:
- id: grounded-quality
  decision: quality = deterministic verdict vs ground truth + risk-required roles present
  rollback: none needed
- id: no-blended-score
  decision: axes aggregated and gated separately
  rollback: none needed
- id: safety-never-tolerated
  decision: any safety regression rejects regardless of savings
  rollback: none needed
- id: replay-rebuilds-plan
  decision: stored decision without economy -> build_routing_plan -> current profile policy
  rollback: none needed
- id: opt-in-quality-floor
  decision: quality_floor null by default; set -> below floor excluded, champions by cost
  rollback: unset quality_floor
- id: reviewer-accepts-sensitive
  decision: task-review accepts sensitive risk so the risk-required reviewer exists for sensitive tasks
  rollback: restore accepted_risks [read_only]
---
# architecture

The matrix drives the existing runtime with the fake adapter; gate, replay and ROI read reports and stored runs only.
