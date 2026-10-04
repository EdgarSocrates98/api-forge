---
sdd: 1
feature: API_FORGE_EVOLUTION1_GOVERNED_BUDGETS
phase: contract
profile: critical
status: done
upstream:
  path: intent.md
  sha256: "c93cc9f2a602bac6f23ebdb9d84ea01f499898800cc973e48bdc0324f9731908"
covers:
  - hierarchical-budget-contracts
  - append-only-admission
  - cli-mcp-budget-parity
  - token-unknown-refusal
  - documentation-and-evidence
---

# contract

New closed contracts:

- `AgenticBudgetPlan/v1` declares immutable task/phase/role/tool limits;
- `BudgetSpend/v1` records one measured append-only cost;
- `BudgetDecision/v1` preserves admission, exhaustion and unresolved-token
  outcomes with an `AF-*` code, field and unlock.

The existing `CostVector/v1` remains the sole cost measurement vocabulary.
