# CapsuleBudget/v1

`CapsuleBudget/v1` is the deterministic byte ceiling of a capsule.

| Field | Meaning |
|---|---|
| `context_bytes` | Ceiling for the serialized capsule (minimum 256) |
| `max_level` | Highest level requested, `L0`–`L4` |
| `serialized_bytes` | Measured canonical size of the emitted capsule |
| `reached_level` | Level actually completed; `L2` when refs were cut by the budget |

A fixed reserve is kept for the refusal entry so a partial capsule stays under
the ceiling unless the L0–L2 envelope alone exceeds it.
