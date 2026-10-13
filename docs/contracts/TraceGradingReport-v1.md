# TraceGradingReport-v1

§23 trace grading over a set of recorded traces.

| Field | Meaning |
|---|---|
| `rubric_id` | the applied rubric |
| `grades` | per-trace `TraceGrade` |
| `unresolved` | traces that could not be graded |

Invariant: grades are computed, never narrated.
