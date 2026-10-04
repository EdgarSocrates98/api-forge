---
sdd: 1
feature: API_FORGE_EVOLUTION1_GOVERNED_BUDGETS
phase: discover
profile: critical
status: done
approaches:
  - id: implicit-counters
    summary: attach ad hoc counters to each caller
    verdict: refused -- loses hierarchy and makes admission non-uniform
  - id: provider-billing
    summary: derive budgets from provider billing or model metadata
    verdict: refused -- external, non-deterministic and outside the offline boundary
  - id: append-only-governor
    summary: apply declared limits to measured CostVector receipts before append
    verdict: chosen -- deterministic, local and evidence-preserving
chosen: append-only-governor
---

# discover

The repository already has `BudgetEnvelope/v1`, `PhaseBudgetPlan/v1`, an
economy ledger and run checkpoints. The missing capability is a single
hierarchical admission point that applies task, phase, role and tool limits to
measured `CostVector` values before a spend is appended.

Decision: add a provider-free append-only budget plan/spend journal and a
deterministic governor. Token limits are enforced only from observed token
measurements; unknown token counts remain unresolved.
