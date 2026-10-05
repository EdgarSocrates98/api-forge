# KnowledgeDrift-v1

§29 rollup between a pack declaration and read-only observation receipts.

| Field | Meaning |
|---|---|
| `domain`/`pack_version` | the pack under evaluation |
| `state` | `verified`/`fresh`/`stale`/`deprecated`/`conflicted`/`unresolved`/`unknown` |
| `signals` | the gate path taken (agreement, delegation, no-receipts) |
| `conflicts` | each pair of receipts that disagree and why |
| `unresolved` | missing inputs, named |
| `observations` | receipt count |

Invariant: zero receipts resolve to `unresolved`; disagreeing receipts
resolve to `conflicted` — never averaged into a fake state.
