# ToolPage/v1

§42 the standardized large-response shape.

| Field | Meaning |
|---|---|
| `summary` | what the whole set is |
| `items` | the bounded window |
| `refs` | full artifacts behind `ctx://`/paths |
| `evidence` | supporting records |
| `unresolved` | what could not be represented |
| `pagination` | `offset`/`limit`/`total`/`next_offset` |

Invariant: `pagination.total` always reports the real cardinality; the
window never pretends to be the whole set.
