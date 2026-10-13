---
sdd: 1
feature: API_FORGE_ECONOMY_EVAL_INTEGRITY
phase: benchmark
profile: critical
status: draft
upstream:
  path: secure.md
  sha256: "35f0a2a8525fddeccbd234bc8806fc19e3e7508875a3609fe50f4aac703e68f9"
baseline: economy evals on main @ 6d2f263
results:
- all ten economy evals pass
- agentic-quality floor 1.0 met by every profile on the recorded corpus
- economy-hardening passes on production code and fails under a mutated plan_roles
---

# benchmark

Measured by the eval commands and stored as evidence; certification gates now fail on the bugs they certify against.
