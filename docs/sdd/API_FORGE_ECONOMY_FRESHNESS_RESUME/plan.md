---
sdd: 1
feature: API_FORGE_ECONOMY_FRESHNESS_RESUME
phase: plan
profile: standard
status: draft
upstream:
  path: architecture.md
  sha256: "08ba042f863a865cbafe6155e587e5425ab4d335b5f04c5f32b0ee0fea42cfb1"
tasks:
- id: contracts
  covers:
  - FreshnessWatch/v1
  - LiveEvidenceDecision/v1
  - VerificationEscalation/v1
  - PhaseBudgetPlan/v1
  - EconomyCheckpoint/v1
  test: sdd/API_FORGE_ECONOMY_FRESHNESS_RESUME/evidence/economy-freshness-tests.txt
  risk: low
  rollback: remove contracts/economy_resume.py
- id: verbs
  covers:
  - freshness-watch
  - live-evidence-gate
  - progressive-verification
  - phase-budgets
  - resume-checkpoint
  test: sdd/API_FORGE_ECONOMY_FRESHNESS_RESUME/evidence/economy-freshness-tests.txt
  risk: low
  rollback: remove the new modules and cli_resume.py
- id: eval
  covers:
  - freshness-eval
  test: sdd/API_FORGE_ECONOMY_FRESHNESS_RESUME/evidence/economy-freshness-eval.json
  risk: low
  rollback: remove evals/freshness_resume.py and the corpus
---
# plan

Contracts, the four modules, the supervisor checkpoint, surfaces, eval.
