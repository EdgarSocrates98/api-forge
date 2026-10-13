---
sdd: 1
feature: API_FORGE_STEP11_MODEL_ROUTING_RETRIEVAL
phase: plan
profile: critical
status: done
tasks:
  - id: G1
    covers: [model-routing-contracts, scorecard-and-promotion, retrieval-ladder, semantic-adapter, query-rewrite-gates]
    test: sdd/API_FORGE_STEP11_MODEL_ROUTING_RETRIEVAL/evidence/G1-focused-tests.txt
  - id: G2
    covers: [eval-corpora]
    test: sdd/API_FORGE_STEP11_MODEL_ROUTING_RETRIEVAL/evidence/G2-evals.txt
  - id: G3
    covers: [cli-mcp-surface]
    test: sdd/API_FORGE_STEP11_MODEL_ROUTING_RETRIEVAL/evidence/G3-gates.txt
upstream:
  path: architecture.md
  sha256: "b0cf08c75eec58a04107c1e2a226691c5f9af30394e0910c8edea8d2175e6064"
---

# plan

G1 — contracts, router, scorecard, ladder, semantic adapter, rewrite gates:
focused pytest over `tests/runtime/test_model_router.py`,
`tests/knowledge/test_levels.py` and the knowledge suite.

G2 — eval corpora: `evals model-routing` (constraint refusal, quality
floor, insufficient evaluations) and `evals retrieval` (gold corpus over
lexical/graph/semantic/hybrid).

G3 — surface gates: Ruff + mypy strict over every new module and CLI.
