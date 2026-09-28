# PhaseBudgetPlan/v1

`PhaseBudgetPlan/v1` is `apiforge economy phase-budget --profile <p> [--usage <json>]` (§104). Shares come from `rules/phase_budgets.yaml` and sum to 1.0.

| Field | Meaning |
|---|---|
| `profile` | Economy profile whose envelope is split |
| `total_calls` / `total_context_bytes` | The profile envelope |
| `phases[]` | `{phase, share, calls, context_bytes, protected, used_calls, used_context_bytes, status}`; calls sum to the envelope and protected phases (contract, verify, secure) get at least one |
| `phases[].status` | `within`, `exceeded`, `protected_overrun` (reported, never cut) or `unmeasured` |
| `status` | `unresolved` when a non-protected phase exceeded its budget |
| `codes` | `AF-BUDGET-PHASE-EXCEEDED`, `AF-BUDGET-PHASE-PROTECTED` |
