---
sdd: 1
feature: API_FORGE_ECONOMY_EXTRAS
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "11d161b6ec51f780c2ba4469774522f0442e6be2641e78b609308613b915996a"
tasks:
- id: contracts
  covers:
  - VerificationPlan/v1
  - RetrievalResult/v1
  - EvidenceNode/v1
  - EconomyDoctor/v1
  - ProviderCapability/v1
  - TierDecision/v1
  - PromptEnvelope/v1
  - LocalityPlan/v1
  test: sdd/API_FORGE_ECONOMY_EXTRAS/evidence/economy-extras-tests.txt
  risk: low
  rollback: remove contracts/economy_extras.py
- id: verbs
  covers:
  - verification-plan
  - retrieval
  - evidence-refs
  - economy-doctor
  - provider-tiers
  - stable-prefix
  - locality
  test: sdd/API_FORGE_ECONOMY_EXTRAS/evidence/economy-extras-tests.txt
  risk: low
  rollback: remove the new modules and cli_extras.py
- id: eval
  covers:
  - extras-eval
  test: sdd/API_FORGE_ECONOMY_EXTRAS/evidence/economy-extras-eval.json
  risk: low
  rollback: remove evals/extras.py and the corpus
---
# plan

Contracts, the seven modules, surfaces, eval.
