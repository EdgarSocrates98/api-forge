---
sdd: 1
feature: API_FORGE_STEP11_MODEL_ROUTING_RETRIEVAL
phase: architecture
profile: critical
status: done
files:
  - src/apiforge/contracts/model_routing.py
  - src/apiforge/contracts/registry.py
  - src/apiforge/contracts/__init__.py
  - src/apiforge/runtime/model_router.py
  - src/apiforge/runtime/model_scorecard.py
  - src/apiforge/knowledge/semantic.py
  - src/apiforge/knowledge/levels.py
  - src/apiforge/knowledge/rewrite.py
  - src/apiforge/rules/model_router.yaml
  - src/apiforge/rules/retrieval_levels.yaml
  - src/apiforge/cli_route.py
  - src/apiforge/cli.py
  - src/apiforge/mcp/tools.py
  - src/apiforge/evals/model_routing.py
  - src/apiforge/evals/retrieval.py
  - evals/corpus/model-routing/
  - evals/corpus/retrieval/
  - tests/runtime/test_model_router.py
  - tests/knowledge/test_levels.py
  - docs/contracts/
decisions:
  - "hard constraints gate eligibility before any scoring; a failed
    constraint produces a ranked entry with eligible=false and reasons,
    never a silent drop"
  - "scorecards constrain and inform — below quality_floor with enough
    evaluations a candidate cannot compete; a missing scorecard lowers the
    score but never blocks"
  - "scorecard fold is deterministic means over declared ModelEvaluation
    rows per provider/model/task_class; unobserved metrics stay null"
  - "the retrieval ladder is data-driven from retrieval_levels.yaml: L0
    exact, L1 lexical, L2 structural graph, L3 hybrid semantic, L4 reranker;
    it stops at the first level meeting min_hits/min_score"
  - "L3 runs only through a declared SemanticAdapter; HashFeatureSimilarityAdapter
    is the local deterministic implementation — no vector DB, no network"
  - "query rewriting is a pure gate evaluation — deterministic failed +
    budget remaining + profile allows; economy blocks"
  - "route promote feeds the phase-5 PromotionEvidence path, so model
    routing inherits shadow→assisted→active instead of inventing a second
    promotion plane"
upstream:
  path: contract.md
  sha256: "16e88a00a226afda7bbdefa623fc3b6635d982b4550f034ef1d8147c7ed090ed"
---

# architecture

Additive modules beside the existing lexical retrieval and scorecard
routing. Nothing mutates `knowledge/retrieval.py` search semantics, the
phase-5 control plane, or provider pricing tables.
