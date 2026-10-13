# TokenLedger/v1

§19 run rollup: Provider Usage -> Token Ledger -> Agent/Task/Run budgets.
Per-basis totals at run, task and agent granularity.

| Field | Meaning |
|---|---|
| `run_id` | Owning run |
| `observed` / `estimated` | `TokenTotals/v1` per basis — separate sums, always |
| `unresolved_entries` | Rows whose usage is unknown — counted, never added |
| `by_task` / `by_agent` | Scoped rollups, still per basis |
| `cost_basis_missing` | Models that carried usage without a pricing row |

Invariant: an `unresolved` entry contributes only to
`unresolved_entries`; the totals it never touches stay honest.
