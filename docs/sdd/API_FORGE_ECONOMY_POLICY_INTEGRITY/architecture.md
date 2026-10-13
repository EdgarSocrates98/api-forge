---
sdd: 1
feature: API_FORGE_ECONOMY_POLICY_INTEGRITY
phase: architecture
profile: critical
status: draft
upstream:
  path: contract.md
  sha256: "fa3cfa0ee48d58955d3038d7c08c3186fabd044e6b1b59a2d5d3855d7975335e"
files:
- src/apiforge/contracts/economy_evals.py
- src/apiforge/evals/agentic_quality.py
- src/apiforge/economy/run_ledger.py
- .github/CODEOWNERS
- scripts/github_ruleset_plan.py
decisions:
- id: same-experiment-baseline
  decision: baseline identity must match unless cross corpus is explicitly allowed and recorded
  rollback: drop the identity check
- id: fail-closed-policy
  decision: schema, non-empty, no blank or duplicate prefixes
  rollback: none needed
- id: read-only-governance
  decision: the ruleset plan never calls GitHub; the owner applies it
  rollback: delete the script
---
# architecture

P1 certification integrity, P2 governance materialization.
