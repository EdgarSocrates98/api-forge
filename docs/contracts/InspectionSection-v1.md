# InspectionSection/v1

§54 one named report section inside `RunInspection`.

| Field | Meaning |
|---|---|
| `name` | Section id (`context`, `memory`, `tools`, `models`, …) |
| `metrics` | Ordered `InspectionMetric` rows |

Invariant: a section exists even when every metric inside it is `unresolved`.
