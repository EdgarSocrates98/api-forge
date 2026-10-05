# InspectionMetric/v1

§57 one named metric with its evidence basis.

| Field | Meaning |
|---|---|
| `name` | Metric id (`context_precision`, `duplicate_context_ratio`, `model_latency_ms`, …) |
| `value` | Numeric/string value; `null` iff `state` is `unresolved` |
| `state` | `observed` (ledger/span proves it) or `unresolved` (source absent) |
| `detail` | Basis or reason, always human-readable |

Invariant: `unresolved` metrics carry `value: null` and a `detail` naming the
missing source.
