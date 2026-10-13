---
sdd: 1
feature: API_FORGE_ECONOMY_ARCH_HARDENING
phase: intent
profile: critical
status: draft
upstream:
  path: discover.md
  sha256: "b61d64541bb3b1a64fdb78c55851b39235bf03d35ea7819d26f03e13effdce20"
problem: 'Economy claims (hard budget, observed tokens, verified proof, safe context) were intentions,
  not code invariants: out-of-root reads into ctx://, per-instance context shares, uncounted shadow calls,
  partial token totals and substring early stops.'
success:
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
out_of_scope:
- new-economy-features
- live-model-calls-in-core
owner: api-forge-economy
risk_class: high
risk_signals:
- path:src/apiforge/security/source_paths.py
- path:src/apiforge/case/service.py
- path:src/apiforge/runtime/control.py
---
# intent

Make every economy claim an invariant enforced by code, starting with the trust boundary.
