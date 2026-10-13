---
sdd: 1
feature: API_FORGE_ECONOMY_EXTRAS
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "8405de865ca1b78aeb74f8e04f044e7d49549e54c15d11954aecb3ff455c4fc8"
covers:
- VerificationPlan/v1
- RetrievalResult/v1
- EvidenceNode/v1
- EconomyDoctor/v1
- ProviderCapability/v1
- TierDecision/v1
- PromptEnvelope/v1
- LocalityPlan/v1
api_ir:
  input: changed files and risk, queries, evidence refs, local state, capability and risk, workspace manifest
  output: plans, ranked passages, evidence nodes, doctor findings, tier decisions, prompt envelopes, locality
    tiers
---
# contract

`RoleContext` and `AgentRequest` gain optional `prompt_prefix_sha256`; everything else is new.
