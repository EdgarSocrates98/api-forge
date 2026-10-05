# ComparisonAxis/v1

§55 one comparison axis.

| Field | Meaning |
|---|---|
| `axis` | Axis id |
| `a`/`b` | Values on each side (`null` when unresolved) |
| `delta` | `b - a`; `null` when either side is unresolved |
| `verdict` | `a`, `b`, `tie` or `unresolved` |
| `detail` | Axis direction and semantics (e.g. lower-is-better) |

Invariant: direction is deterministic — tokens/cost/latency/context prefer
lower; quality/evidence prefer higher.
