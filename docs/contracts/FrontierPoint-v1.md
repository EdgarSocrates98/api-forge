# FrontierPoint-v1

§23 quality × cost × latency for one profile.

| Field | Meaning |
|---|---|
| `profile` | profile name |
| `quality`/`latency_ms`/`cost` | axis values — `null` means unmeasured |
| `cost_state` | `observed`/`unresolved` — `null` cost must be unresolved |
| `pareto` | Pareto-optimal over observed axes |
| `detail` | unresolved note |

Invariant: unresolved cost never carries a value; observed cost must.
