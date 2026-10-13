# ReconciliationAxis/v1

One side of a §22 reconciliation — either the declared estimate or the
ledger-derived observation.

| Field | Meaning |
|---|---|
| `tokens` | Total tokens for the scope |
| `cost` | Total cost (priced, same currency on both sides) |
| `tool_calls` | Tool-call count (observed: rows carrying tool bytes) |
| `elapsed_ms` | Elapsed time in milliseconds (observed: summed row durations) |

Every field is optional: `null` means the value was never recorded, and
the axis lands in the reconciliation's `unresolved` list rather than
being silently treated as zero.
