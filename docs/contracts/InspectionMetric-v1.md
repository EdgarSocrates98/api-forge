# InspectionMetric/v1

§57 one named metric with its evidence basis.

| Field | Meaning |
|---|---|
| `name` | Metric id (`context_precision`, `duplicate_context_ratio`, `model_latency_ms`, …) |
| `value` | Numeric/string value; `null` iff `state` is `unresolved` |
| `state` | `observed` (all eligible source rows measured), `partial` (some eligible rows measured), `estimated` or `unresolved` |
| `detail` | Basis or reason, always human-readable |

Invariant: `unresolved` metrics carry `value: null` and a `detail` naming the
missing source. A partial metric carries the observed value plus the measured
row/denominator basis; it is never presented as complete observation.
