---
sdd: 1
feature: API_FORGE_ECONOMY_EVAL_INTEGRITY
phase: intent
profile: critical
status: draft
upstream:
  path: discover.md
  sha256: "3982c873d201bf2464803ed80fd1d68c430f08d92e7bf82c904709a4c86c705a"
problem: 'The certification layer could certify wrong outcomes: equally wrong profiles passed,
  deterministic rows made measured runs look partial, persist failures leaked across runs, the hardening
  oracle re-implemented the logic it guards and explicit paths bypassed the trust boundary.'
success:
- quality-floor
- baseline-non-regression
- token-eligibility
- run-scoped-failures
- production-oracle
- explicit-path-confinement
out_of_scope:
- new-economy-features
- floors-for-other-evals
owner: api-forge-economy
risk_class: high
risk_signals:
- path:src/apiforge/security/source_paths.py
- path:src/apiforge/context/delta.py
---
# intent

A green certification must mean "good", and every path a caller passes must obey the same trust boundary.
