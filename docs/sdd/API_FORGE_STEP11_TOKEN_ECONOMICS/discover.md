---
sdd: 1
feature: API_FORGE_STEP11_TOKEN_ECONOMICS
phase: discover
profile: critical
status: done
approaches:
  - id: extend-costvector
    summary: add the five provider token fields onto CostVector and keep
      reading economy.jsonl attribution rows
    verdict: refused -- CostVector is a frozen v1 contract and its
      observed_tokens scalar cannot carry per-field provider usage or the
      observed/estimated/unresolved basis discipline
  - id: price-constants
    summary: ship a small dict of well-known provider rates in source
    verdict: refused -- prompt §21 forbids hardcoded prices; rates must be
      declared versioned data with source and effective_at
  - id: token-economics-plane
    summary: new TokenAccounting/TokenLedger contracts beside the existing
      economy ledgers, a declared ProviderPricing catalog, and a pure
      reconciliation function producing BudgetReconciliation with
      calibration error per axis
    verdict: chosen -- additive, keeps every existing economy surface
      working, and implements §19-§22 without mixing bases
chosen: token-economics-plane
---

# discover

Phase 3 of `prompt_evo_step11.md` (§19-§22): unify token economics into one
pipeline (Provider Usage -> Token Ledger -> Agent/Task/Run Budget -> Provider
Cost -> Economy Report), model provider usage with five token fields and the
observed/estimated/unresolved basis discipline, model provider pricing as
versioned declared data, and reconcile estimate vs observation after each run
with calibration error on tokens, cost, tool calls and elapsed time.

Existing economy pieces are kept intact: `tokens.py` transcript parsing,
`run_ledger` attribution and coverage, `phase_budget`, `governance/budget`
admission. The new plane consumes them and adds the missing per-field,
per-basis rollup plus declared pricing and reconciliation.
