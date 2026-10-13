---
sdd: 1
feature: API_FORGE_ECONOMY_SELECTIVE_AGENTICS
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "d75da05de4758442a869c7248bd39b1927b3ed375b9047a4449f11e20b5e46f5"
covers:
- ExpertiseSelection/v1
- RoleContextPlan/v1
- PositionDelta/v1
- RefereePacket/v1
- ShadowDecision/v1
- AgentUniqueness/v1
api_ir:
  input: TaskSpec target and outcome, envelope context_bytes/shadow_share, debate submissions, agent catalog
  output: role context plans, request context fields, referee packets, shadow decisions, audit rows
---
# contract

`BudgetEnvelope` gains `context_bytes` (default 32000) and `shadow_share` (default 0.0); `AgentRequest` gains optional `context_class`, `context_refs`, `expertise`. `AgentInvocation` and replay digests are unchanged.
