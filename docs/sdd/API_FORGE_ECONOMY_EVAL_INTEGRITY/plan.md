---
sdd: 1
feature: API_FORGE_ECONOMY_EVAL_INTEGRITY
phase: plan
profile: critical
status: draft
upstream:
  path: architecture.md
  sha256: "dc5697fb4147102acde10a6560499aabebeec3924281603537f2c3053449e05e"
tasks:
- id: e1-certification
  covers:
  - quality-floor
  - baseline-non-regression
  - token-eligibility
  - run-scoped-failures
  test: sdd/API_FORGE_ECONOMY_EVAL_INTEGRITY/evidence/eval-integrity-tests.txt
  risk: medium
  rollback: revert the E1 commit
- id: e2-oracle-paths
  covers:
  - production-oracle
  - explicit-path-confinement
  test: sdd/API_FORGE_ECONOMY_EVAL_INTEGRITY/evidence/economy-hardening-eval.json
  risk: high
  rollback: revert the E2 commit
---
# plan

E1 then E2, one commit each, full suite before push.
