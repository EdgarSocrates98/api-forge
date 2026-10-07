# TraceGrade-v1

§23 the graded result for one trace under one rubric.

| Field | Meaning |
|---|---|
| `trace_id`/`rubric_id` | graded subject and rubric identity |
| `dimensions` | per-dimension `TraceGradeDimension` rows |
| `score` | renormalized weighted score over observed dimensions |
| `verdict` | `pass`/`review`/`fail`/`unresolved` |
| `evidence_refs`/`unresolved` | aggregated evidence and unresolved dimensions |

Invariant: empty or mixed-id traces are `unresolved`, never graded.
