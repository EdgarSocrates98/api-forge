# Governed agentic budgets

Wave 2 adds `AgenticBudgetPlan/v1`, `BudgetSpend/v1` and
`BudgetDecision/v1` over the existing `CostVector/v1` economy vocabulary.
Limits are exact and hierarchical:

```text
task -> phase -> role -> tool
```

Every proposed spend is checked against all matching limits before the receipt
is appended to `.apiforge/economy/agentic-budget/spends.jsonl`. A `stop`
decision is an exhaustion proof, not a silent downgrade. If a declared token
limit has no observed token measurement, the result is `unresolved` with
`AF-BUDGET-TOKENS-UNRESOLVED`; bytes never become invented tokens.

The same service is available through CLI and MCP:

```text
apiforge economy budget-plan --plan plan.json --root .
apiforge economy budget-check --plan-id <id> --task-id task-1 \
  --phase build --role builder --tool compile --spend-id spend-1 \
  --cost '{"context_bytes":1200}'
apiforge economy budget-spend --plan-id <id> --spend-id spend-1 \
  --task-id task-1 --phase build --role builder --tool compile \
  --cost '{"context_bytes":1200}' --now 2026-10-04T12:00:00Z
```

Plans and spends are local, append-only and provider-free. Replacing a plan
with the same id but a different content hash is refused; use an explicitly
reviewed new plan id. This governor does not authorize external mutation or
claim production throughput.
