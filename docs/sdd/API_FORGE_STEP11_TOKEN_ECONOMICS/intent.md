---
sdd: 1
feature: API_FORGE_STEP11_TOKEN_ECONOMICS
phase: intent
profile: critical
status: done
risk_class: medium
problem: token accounting is scattered (transcript sums, labeled estimates,
  run-ledger coverage) with no per-field provider usage, no declared versioned
  pricing, and no post-run estimate-vs-observed reconciliation with
  calibration error
success: one TokenLedger rolls up usage per basis at run/task/agent level
  without ever mixing bases, ProviderPricing is declared data resolved by
  effective_at, cost is computed only from declared rates with gaps named,
  and BudgetReconciliation measures calibration error per axis after a run
out_of_scope:
  - live provider prices in the shipped catalog (callers declare their own)
  - automatic usage recording inside runtime dispatch (governor phase 4)
  - mutating the frozen v1 CostVector/RunLedgerEntry payloads
upstream:
  path: discover.md
  sha256: "c80bef4df936bd09a7d448aeeee2ce6387008cbba1d60b6c48ff158dd5208641"
---

# intent
