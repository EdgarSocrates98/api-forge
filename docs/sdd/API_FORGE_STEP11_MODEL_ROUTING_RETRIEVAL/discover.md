---
sdd: 1
feature: API_FORGE_STEP11_MODEL_ROUTING_RETRIEVAL
phase: discover
profile: critical
status: done
approaches:
  - id: inline-provider-tiers
    summary: reuse economy/providers tiers T0-T3 directly as the model router
    verdict: refused -- the tier table prices tokens, it does not declare
      tool support, structured output, context window or reasoning tier;
      §33 needs capability constraints, not just cost
  - id: scorecard-only-rank
    summary: rank purely on ModelScorecard quality history
    verdict: refused -- a candidate failing a hard constraint (no tool
      support, too small a window) must be ineligible regardless of score;
      §34 scorecards are a floor, not the whole decision
  - id: declared-candidates-constraints-then-score
    summary: declared ModelCandidate rows in rules yaml; hard constraints
      first (ineligible candidates ranked with reasons), then a weighted
      score over quality history, latency, cost and availability; adaptive
      retrieval as a separate L0-L4 ladder that stops at the first
      sufficient level
    verdict: chosen -- deterministic, honest refusals, cost-aware without
      letting cheap models win on price alone
chosen: declared-candidates-constraints-then-score
---

# discover

Phase 6 of `prompt_evo_step11.md` (§33-§39): an adaptive model router that
reasons over declared capabilities and measured scorecards; an adaptive
retrieval ladder L0-L4 that climbs only on insufficiency; optional semantic
retrieval through a declared local adapter; retrieval evals comparing
strategies; and gated query rewriting.
