---
sdd: 1
feature: API_FORGE_ECONOMY_ROUTING
phase: architecture
profile: standard
status: draft
upstream:
  path: contract.md
  sha256: "fef08b834f06ec5bb49aa8fd2fd5386ea496e393ff06bf331201e28381ded8b3"
files:
  - src/apiforge/contracts/economy.py
  - src/apiforge/contracts/routing.py
  - src/apiforge/contracts/workspace.py
  - src/apiforge/rules/economy_profiles.yaml
  - src/apiforge/runtime/economy.py
  - src/apiforge/runtime/supervisor.py
  - src/apiforge/runtime/runner.py
  - src/apiforge/sdd/risk.py
  - src/apiforge/sdd/checks.py
  - src/apiforge/sdd/profiles.yaml
  - src/apiforge/evals/economy_routing.py
decisions:
  - id: staged-execution
    decision: L2 runs primary plus risk-required roles concurrently; optional review, debate and gate escalate only on deterministic triggers
    rollback: call execute_run with economy_enabled=False
  - id: single-enforcement-point
    decision: effective policy caps calls at min(policy, TaskSpec, envelope) with a verification reserve
    rollback: drop _effective_policy
  - id: escalate-only
    decision: effective profile is max(requested, risk floor)
    rollback: remove floors from economy_profiles.yaml
  - id: l0-proof
    decision: a complete deterministic task run covering expected_proofs stops the run before agent calls; acceptance stays separate
    rollback: skip deterministic_proof
  - id: explicit-unresolved
    decision: exhaustion and ceilings keep final_status REVIEW and report economy.status unresolved with a cataloged code
    rollback: none needed
  - id: resume-no-retrim
    decision: resume applies the call cap only; it never re-trims roles of an already planned control run
    rollback: none needed
---
# architecture

contracts → runtime/economy → runtime/routing plan → runtime/supervisor →
CLI/MCP. `sdd/risk` depends only on contracts and `contract_intel`.
