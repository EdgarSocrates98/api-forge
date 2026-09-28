---
sdd: 1
feature: API_FORGE_ECONOMY_POLICY_INTEGRITY
phase: plan
profile: critical
status: draft
upstream:
  path: architecture.md
  sha256: "e2ed68501ea40aa342a024f9d30736b434e4682650db047e88999055f6a20563"
tasks:
- id: p1-benchmark-policy
  covers:
  - benchmark-identity
  - strict-baseline
  - fail-closed-token-policy
  test: sdd/API_FORGE_ECONOMY_POLICY_INTEGRITY/evidence/policy-integrity-tests.txt
  risk: medium
  rollback: revert the P1 commit
- id: p2-governance
  covers:
  - codeowners
  - ruleset-plan
  test: sdd/API_FORGE_ECONOMY_POLICY_INTEGRITY/evidence/ruleset-plan.json
  risk: high
  rollback: revert the P2 commit
---
# plan

P1 then P2, full suite before push.
