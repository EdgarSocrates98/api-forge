---
sdd: 1
feature: API_FORGE_ECONOMY_ROUTING
phase: discover
profile: standard
status: draft
approaches:
  - id: economy-assessment
    summary: EconomyPlan/BudgetEnvelope as another routing assessment enforced by the supervisor
    verdict: chosen -- follows the risk/graph/scorecard assessment pattern and keeps RoutingPlan lean
  - id: extend-routing-plan
    summary: budget and profile fields directly on RoutingPolicy/RoutingPlan
    verdict: refused -- mixes cost preference with role decisions and weakens explanations
  - id: pre-router-filter
    summary: profile filters candidates before eligibility and ranking
    verdict: refused -- Wave 4 scope and harder risk invariant
chosen: economy-assessment
---
# discover

Source: `prompt_evo_economy.md` §11–§19, §33–§35, §65 and the archived Wave 0/1
feature. The supervisor already bounds calls and flags debate rooms; routing
already derives required roles from risk and graph impact.
