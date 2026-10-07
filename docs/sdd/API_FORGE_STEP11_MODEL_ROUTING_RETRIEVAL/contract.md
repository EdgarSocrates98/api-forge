---
sdd: 1
feature: API_FORGE_STEP11_MODEL_ROUTING_RETRIEVAL
phase: contract
profile: critical
status: done
covers:
  - model-routing-contracts
  - scorecard-and-promotion
  - retrieval-ladder
  - semantic-adapter
  - query-rewrite-gates
  - eval-corpora
  - cli-mcp-surface
contracts:
  - ModelRouteInputs/v1
  - ModelCandidate/v1
  - RankedModel/v1
  - ModelRouteDecision/v1
  - ModelEvaluation/v1
  - ModelScorecard/v1
  - RetrievalStep/v1
  - AdaptiveRetrievalResult/v1
  - QueryRewrite/v1
  - RetrievalComparison/v1
upstream:
  path: intent.md
  sha256: "3ef9410d52e1ac3270f92352e19dded482b6bdab620c111b4851d38d35fae025"
---

# contract

Ten versioned contracts. `ModelRouteInputs`/`ModelCandidate`/
`ModelRouteDecision`/`RankedModel` describe the routing decision;
`ModelEvaluation`/`ModelScorecard` the §34 quality history;
`RetrievalStep`/`AdaptiveRetrievalResult` the ladder;
`QueryRewrite` the gated rewrite record; `RetrievalComparison` the §38
eval metrics.

Invariants:

- `ModelRouteDecision.routing_kind` is `"model"` — separate from capability
  and agent routing;
- every ranked candidate lists its refusal `reasons`, never dropped
  silently;
- `ModelScorecard` metrics never observed stay `null` and are named in
  `unresolved` — never zeroed;
- `AdaptiveRetrievalResult` records every attempted step in order; the
  ladder never reports a level it did not run;
- `QueryRewrite.rewritten` is `null` on any gate block — original and
  rewritten are always both recorded when a rewrite happens;
- `RetrievalComparison.cost` is `null` with `cost_rate` in `unresolved`
  when no rate was declared.
