# ContextQualityMetric/v1

One metric of the closed `ContextMetricKind` catalog (14 kinds, always all
emitted on a report): precision, recall, required-evidence recall, density, duplicate,
irrelevant, stale, expansion rate, reuse rate, cache hit rate, role
efficiency, selected-evidence utilization, evidence per token and useful facts
per 1k tokens.

| Field | Meaning |
|---|---|
| `name` | Closed metric kind |
| `value` | Measured ratio/count; `null` iff `basis` is `unresolved` |
| `unit` | `ratio` unless declared otherwise |
| `basis` | `observed` (recorded inputs), `estimated` (declared approximation) or `unresolved` (input never recorded) |
| `detail` | Human-readable numerator/denominator provenance; evidence recall requires the declared required evidence set |

`evidence_recall` stays `unresolved` until `required_evidence_uris` (or
required evidence refs) are declared; explicitly declared missing URIs remain
in its denominator. `selected_evidence_utilization` is a separate selected-set
metric. `useful_facts_per_1k_tokens` stays
`unresolved` until fact IDs, not merely context refs, are recorded.

Invariant (enforced by the contract): unresolved metrics carry no value;
observed/estimated metrics require one.
