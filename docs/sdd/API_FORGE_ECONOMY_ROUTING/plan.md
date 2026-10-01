---
sdd: 1
feature: API_FORGE_ECONOMY_ROUTING
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "bc5e596c5b3234ade8f45f362b8e4c65de1ab9a8be4a11fd229752fee947167f"
tasks:
  - id: contracts
    covers: [BudgetEnvelope/v1, EconomyPlan/v1, LadderStep/v1, RiskClassification/v1]
    test: sdd/API_FORGE_ECONOMY_ROUTING/evidence/economy-routing-tests.txt
    risk: low
    rollback: remove the new contracts and optional fields
  - id: economy-plane
    covers: [economy-profiles, risk-floor-invariant, supervisor-envelope, stop-and-ladder]
    test: sdd/API_FORGE_ECONOMY_ROUTING/evidence/economy-routing-tests.txt
    risk: medium
    rollback: run the supervisor with economy_enabled=False
  - id: risk-adaptive-sdd
    covers: [risk-adaptive-sdd]
    test: sdd/API_FORGE_ECONOMY_ROUTING/evidence/economy-routing-tests.txt
    risk: low
    rollback: remove sdd/risk.py, the micro profile and the below-risk check
  - id: eval
    covers: [economy-routing-eval]
    test: sdd/API_FORGE_ECONOMY_ROUTING/evidence/economy-routing-eval.json
    risk: low
    rollback: remove evals/economy_routing.py and the corpus
---
# plan

Contracts, then the economy module, supervisor staging, surfaces, SDD
classification and the corpus. Targeted tests per task; full suite once.
