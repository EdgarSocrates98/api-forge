---
sdd: 1
feature: API_FORGE_STEP11_MODEL_ROUTING_RETRIEVAL
phase: ship
profile: critical
status: done
deviations:
  - "ModelRouteDecision is emitted by route model; wiring a runtime
    dispatcher to consume it per request is left for a later phase"
  - "HashFeatureSimilarityAdapter is deterministic local feature similarity,
    retrieval; a production embedding service would plug the same
    SemanticAdapter protocol"
  - "query rewriting is evaluated at the CLI boundary; the retrieval engine
    does not auto-rewrite"
evidence:
  - docs/sdd/API_FORGE_STEP11_MODEL_ROUTING_RETRIEVAL/evidence/G1-focused-tests.txt
  - docs/sdd/API_FORGE_STEP11_MODEL_ROUTING_RETRIEVAL/evidence/G2-evals.txt
  - docs/sdd/API_FORGE_STEP11_MODEL_ROUTING_RETRIEVAL/evidence/G3-gates.txt
rollback: "revert this commit; all modules are additive — lexical retrieval,
  scorecard routing and the control plane are untouched and older code
  never opens rules/model_router.yaml or rules/retrieval_levels.yaml"
upstream:
  path: benchmark.md
  sha256: "9e1670950010f28379f01d4a23961c604b018bb7f19c10b96cb957c5e2e23ec3"
---

# ship

Phase 6 delivered: deterministic model routing over declared candidates
with §34 scorecard floors, promotion through the phase-5 lifecycle, the
L0-L4 adaptive retrieval ladder with optional local semantic, §38 strategy
evals and §39-gated query rewriting.
