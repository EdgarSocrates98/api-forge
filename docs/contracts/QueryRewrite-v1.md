# QueryRewrite/v1

§39 original vs rewritten query — gated, never silent.

| Field | Meaning |
|---|---|
| `original` / `rewritten` | Both strings recorded; `rewritten` is `null` when a gate blocked |
| `gate` | `allowed`, `deterministic_succeeded`, `budget_blocked` or `profile_blocked` |
| `reason` | Why the gate resolved as it did |

A rewrite is allowed only when deterministic retrieval failed, the declared
budget still has room, and the profile permits it (economy blocks).
