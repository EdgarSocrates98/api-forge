---
sdd: 1
feature: API_FORGE_STEP11_EVAL_PLANE
phase: ship
profile: critical
status: done
deviations:
  - "live provider execution stays deferred_external per the roadmap boundary — the layer ships a declared descriptor and report shape, not an adapter"
  - "frontier cost requires provider-accounted input files — without them every profile reports cost_state unresolved by design"
  - "the adversarial corpus is synthetic and offline; real-world payload expansion is a human-curated addition, not generated at runtime"
evidence:
  - docs/sdd/API_FORGE_STEP11_EVAL_PLANE/evidence/G1-focused-tests.txt
  - docs/sdd/API_FORGE_STEP11_EVAL_PLANE/evidence/G2-evals.txt
  - docs/sdd/API_FORGE_STEP11_EVAL_PLANE/evidence/G3-gates.txt
rollback: "revert this commit; all modules, verbs, corpora and docs are
  additive — the governed runtime, memory, trust and MCP surfaces are
  unchanged and older eval waves are untouched"
upstream:
  path: benchmark.md
  sha256: "9e5caa2c5632a32c4953d87903c1152ab4d54000f4aec74786d4a82fa49545d3"
---

# ship

Phase 11 delivered: rubric-driven trace grading with unresolved
honesty, a 9/9 synthetic security-adversarial corpus with zero escapes,
a 9/9 memory eval wave over the real persistence gates, a
quality/cost/latency frontier that never fabricates provider numbers,
the honest live-eval layer with provider_tier deferred_external, and
the agentic threat model documenting trust boundaries and controls.
