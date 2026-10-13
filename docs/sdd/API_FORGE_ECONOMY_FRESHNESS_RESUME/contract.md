---
sdd: 1
feature: API_FORGE_ECONOMY_FRESHNESS_RESUME
phase: contract
profile: standard
status: draft
upstream:
  path: intent.md
  sha256: "9d2dd778efc3020f30596444f7db60635cdadc0345751dec92807951229cacbe"
covers:
- FreshnessWatch/v1
- LiveEvidenceDecision/v1
- VerificationEscalation/v1
- PhaseBudgetPlan/v1
- EconomyCheckpoint/v1
api_ir:
  input: upstream manifest and clock, question and requested mode, static/test/runtime verdicts or a TestSlice, profile and per-phase usage, runtime run directory
  output: watch entries, evidence decision, next verification step, phase budgets, economy checkpoint
---
# contract

`PackFreshness` gains optional `source_version`, `expires_at` and `upstream`; resume output gains an `economy` block. Everything else is new.
