# ContextQualityMetric/v1

One metric of the closed `ContextMetricKind` catalog (13 kinds, always all
emitted on a report): precision, recall, evidence recall, density, duplicate,
irrelevant, stale, expansion rate, reuse rate, cache hit rate, role
efficiency, evidence per token and useful facts per 1k tokens.

| Field | Meaning |
|---|---|
| `name` | Closed metric kind |
| `value` | Measured ratio/count; `null` iff `basis` is `unresolved` |
| `unit` | `ratio` unless declared otherwise |
| `basis` | `observed` (recorded inputs), `estimated` (declared approximation) or `unresolved` (input never recorded) |
| `detail` | Human-readable numerator/denominator provenance |

Invariant (enforced by the contract): unresolved metrics carry no value;
observed/estimated metrics require one.
