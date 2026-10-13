# TraceGradeDimension-v1

§23 one rubric dimension scored over one trace.

| Field | Meaning |
|---|---|
| `dimension/weight` | declared rubric identity and weight from `rules/trace_rubric.yaml` |
| `score` | [0,1] when `state=observed`; always `null` when `unresolved` |
| `state` | `observed`/`unresolved` |
| `signals_found`/`signals_missing` | measured evidence of what the dimension saw |
| `detail` | unresolved reason — required when `unresolved` |

Invariant: unresolved dimensions carry a reason and never a score.
