---
sdd: 1
feature: API_FORGE_ECONOMY_ARCH_HARDENING
phase: build
profile: critical
status: draft
upstream:
  path: plan.md
  sha256: "7acaddbe46385c373442b94ea015573c0a94f8c75302f817d19d6ba7293e71f6"
tasks:
- id: h1-trust-boundary
  status: done
  evidence: sdd/API_FORGE_ECONOMY_ARCH_HARDENING/evidence/hardening-tests.txt
- id: h2-budgets-accounting
  status: done
  evidence: sdd/API_FORGE_ECONOMY_ARCH_HARDENING/evidence/hardening-tests.txt
- id: h3-proof-cache
  status: done
  evidence: sdd/API_FORGE_ECONOMY_ARCH_HARDENING/evidence/hardening-tests.txt
- id: h4-reporting-evals-ci
  status: done
  evidence: sdd/API_FORGE_ECONOMY_ARCH_HARDENING/evidence/economy-hardening-eval.json
claims:
- trust-boundary
- context-budget-invariant
- call-accounting
- token-coverage
- structured-proofs
- cache-fall-through
- knowledge-generation
- honest-reporting
- scoped-evals
- ci-on-main
---
# build

Implemented the resolver and verified case reader, class-pool budgets with contract validators, ControlPlane shadow accounting and shadow modes, token coverage and auditable ledger rows, structured L0 proofs, cache fall-through and timestamp validation, knowledge generation keys and Unicode retrieval, phase/delta/routing reporting, `evals economy-hardening`, `evals agentic-quality`, matrix `claim_scope` and the CI token/schedule fix.
