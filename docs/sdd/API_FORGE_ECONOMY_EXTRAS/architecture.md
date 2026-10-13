---
sdd: 1
feature: API_FORGE_ECONOMY_EXTRAS
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "f2335c66b0922468f6b81d5e1d95e520fac94c07b0f542368d1f3a7af52321f1"
files:
- src/apiforge/contracts/economy_extras.py
- src/apiforge/verification/selection.py
- src/apiforge/knowledge/retrieval.py
- src/apiforge/rules/query_expansion.yaml
- src/apiforge/evidence/resolve.py
- src/apiforge/economy/doctor.py
- src/apiforge/economy/providers.py
- src/apiforge/rules/providers.yaml
- src/apiforge/runtime/prompting.py
- src/apiforge/workspace/locality.py
- src/apiforge/cli_extras.py
- src/apiforge/evals/extras.py
decisions:
- id: plan-never-executes
  decision: verify plan prints commands and reasons; CI runs them
  rollback: none needed
- id: ladder-floor-from-risk
  decision: micro V1, low V2, medium V4, high V5; empty selection escalates to V5
  rollback: none needed
- id: one-hop-evidence
  decision: evidence refs resolve one node and neighbor refs
  rollback: none needed
- id: no-evidence-no-downgrade
  decision: T1 only with a fresh promoted scorecard at the quality floor
  rollback: none needed
- id: run-free-prefix
  decision: prompt prefix excludes timestamps, run ids and paths
  rollback: drop prompt_prefix_sha256
---
# architecture

Each verb reads local artifacts and returns a contract; the supervisor only gains the prefix hash on requests.
