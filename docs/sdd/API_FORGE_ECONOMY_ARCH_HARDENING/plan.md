---
sdd: 1
feature: API_FORGE_ECONOMY_ARCH_HARDENING
phase: plan
profile: critical
status: draft
upstream:
  path: architecture.md
  sha256: "c71fdd920664e928cc6183d1c67df47e7d6be707364b83a574843e536b1a4a21"
tasks:
- id: h1-trust-boundary
  covers:
  - trust-boundary
  test: sdd/API_FORGE_ECONOMY_ARCH_HARDENING/evidence/hardening-tests.txt
  risk: high
  rollback: revert the H1 commit
- id: h2-budgets-accounting
  covers:
  - context-budget-invariant
  - call-accounting
  - token-coverage
  test: sdd/API_FORGE_ECONOMY_ARCH_HARDENING/evidence/hardening-tests.txt
  risk: high
  rollback: revert the H2 commit
- id: h3-proof-cache
  covers:
  - structured-proofs
  - cache-fall-through
  - knowledge-generation
  test: sdd/API_FORGE_ECONOMY_ARCH_HARDENING/evidence/hardening-tests.txt
  risk: medium
  rollback: revert the H3 commit
- id: h4-reporting-evals-ci
  covers:
  - honest-reporting
  - scoped-evals
  - ci-on-main
  test: sdd/API_FORGE_ECONOMY_ARCH_HARDENING/evidence/economy-hardening-eval.json
  risk: medium
  rollback: revert the H4 commit
---
# plan

Four waves, one commit each, full suite before push.
