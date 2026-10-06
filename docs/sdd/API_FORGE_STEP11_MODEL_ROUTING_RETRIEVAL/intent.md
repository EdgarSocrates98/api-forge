---
sdd: 1
feature: API_FORGE_STEP11_MODEL_ROUTING_RETRIEVAL
phase: intent
profile: critical
status: done
risk_class: high
problem: routing picks models without declared capability constraints or
  quality floors — cheap models can win on price alone, retrieval searches
  one fixed depth, there is no semantic path and no governed rewrite, and
  none of it is measured against a gold corpus
success: route model ranks declared candidates with hard constraints first
  and §34 scorecard floors; route promote turns real evaluations into
  phase-5 promotion evidence; knowledge adaptive climbs L0→L4 only until
  sufficient with L3 optional via a declared SemanticAdapter; knowledge
  rewrite is gated by deterministic failure + budget + profile; evals
  compare strategies on recall/precision/latency/tokens/cost
out_of_scope:
  - per-request dispatcher consuming ModelRouteDecision in the runtime loop
  - live provider calls or remote embedding services — adapters stay local
  - a vector database dependency — HashFeatureSimilarityAdapter is deterministic
  - automatic rewrite triggers inside the retrieval engine
upstream:
  path: discover.md
  sha256: "65b25083f06ab80fa116dcf4ee2ff78b83fcc251c8dfeacc1c691b16a833ecd1"
---

# intent

Deliver the §33-§39 wave: deterministic model routing with honest refusals,
scorecard-segmented quality history, phase-5-compatible promotion, an
adaptive retrieval ladder, optional semantic retrieval, retrieval evals and
gated query rewriting — all additive, all offline.
