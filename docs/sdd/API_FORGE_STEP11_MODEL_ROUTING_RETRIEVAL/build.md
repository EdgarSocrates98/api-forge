---
sdd: 1
feature: API_FORGE_STEP11_MODEL_ROUTING_RETRIEVAL
phase: build
profile: critical
status: done
tasks:
  - id: B1
    summary: ten contracts + registry + exports + contract docs + AF codes
    files: [src/apiforge/contracts/model_routing.py, src/apiforge/contracts/registry.py, src/apiforge/contracts/__init__.py, docs/contracts/, docs/catalog-contract.md]
  - id: B2
    summary: deterministic model router + scorecard fold + promotion bridge + declared candidate policy
    files: [src/apiforge/runtime/model_router.py, src/apiforge/runtime/model_scorecard.py, src/apiforge/rules/model_router.yaml]
  - id: B3
    summary: adaptive retrieval ladder + semantic adapter + gated query rewriting + level policy
    files: [src/apiforge/knowledge/levels.py, src/apiforge/knowledge/semantic.py, src/apiforge/knowledge/rewrite.py, src/apiforge/rules/retrieval_levels.yaml]
  - id: B4
    summary: route/knowledge CLI verbs, MCP read tools, both eval corpora, tests
    files: [src/apiforge/cli_route.py, src/apiforge/cli.py, src/apiforge/mcp/tools.py, src/apiforge/evals/model_routing.py, src/apiforge/evals/retrieval.py, evals/corpus/, tests/]
claims:
  - "constraints refuse before scoring: tool/structured/context/reasoning/
    cost/latency/availability failures mark eligible=false with reasons"
  - "a scorecard below quality_floor with min_evaluations blocks the
    candidate from competing on cost; insufficient evaluations is a named
    reason, not a zero"
  - "route promote refuses AF-ROUTE-PROMOTION-EVIDENCE when the scorecard
    lacks min_evaluations or quality_floor — synthetic-only benchmarks
    never promote"
  - "the ladder stops at the first sufficient level; L3 reports
    unresolved=[semantic] when no adapter is declared"
  - "rewrites are gate-evaluated: deterministic failed + budget + profile;
    economy profile blocks with gate=profile_blocked"
  - "no provider calls, no vector DB, no network — everything offline"
upstream:
  path: plan.md
  sha256: "0e2df2b64cd8884622889d932189f13c58777ecd173ed76b8deacd4daf923859"
---

# build

Implementation matches the architecture decisions; every claim above is
exercised by the focused suite or the eval corpora.
