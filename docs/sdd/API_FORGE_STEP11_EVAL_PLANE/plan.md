---
sdd: 1
feature: API_FORGE_STEP11_EVAL_PLANE
phase: plan
profile: critical
status: done
tasks:
  - id: G1
    covers: [trace-grading, rubric-policy, live-eval-layer, provider-deferral, quality-frontier, adversarial-corpus, memory-evals, unresolved-honesty]
    test: sdd/API_FORGE_STEP11_EVAL_PLANE/evidence/G1-focused-tests.txt
  - id: G2
    covers: [eval-corpus, cli-surface]
    test: sdd/API_FORGE_STEP11_EVAL_PLANE/evidence/G2-evals.txt
  - id: G3
    covers: [trace-grading, live-eval-layer, refusal-codes]
    test: sdd/API_FORGE_STEP11_EVAL_PLANE/evidence/G3-gates.txt
upstream:
  path: architecture.md
  sha256: "891f8e646e73d0cf9bcc20480165dda610a763ebb7eaed626b9e2da17e7e0a20"
---

# plan

G1 — focused pytest over the eval plane: rubric loading and scoring,
empty/mixed-trace unresolved behavior, adversarial outcome mapping,
memory-gate seeding, frontier pareto on frozen models and honest
provider deferral. G2 — the four deterministic corpora plus the
frontier fixture and the live-layer report end to end through the CLI.
G3 — Ruff, format check and mypy strict over the new/changed modules.
