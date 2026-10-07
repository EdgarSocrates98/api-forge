---
sdd: 1
feature: API_FORGE_ECONOMY_ROUTING
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "e55d5cacf2ba9c407e1de035799fc07727522cf8852080850386eaf3f9171770"
covers: [BudgetEnvelope/v1, EconomyPlan/v1, LadderStep/v1, RiskClassification/v1]
api_ir:
  input: TaskSpec, requested profile (flag/manifest/policy), routing assessments, change signals
  output: economy plan on the routing decision, economy block in runtime results, risk class for SDD
---
# contract

`RoutingDecision.economy` and `ProjectManifest.economy_profile` are optional
and default to `null`; legacy payloads validate unchanged. `BudgetEnvelope`
forbids `silent_downgrade`.
