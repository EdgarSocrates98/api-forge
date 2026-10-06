# CapsuleRefusal/v1

`CapsuleRefusal/v1` carries a cataloged refusal inside a partial capsule
instead of failing the command.

| Field | Meaning |
|---|---|
| `code` | `AF-*` code from `docs/catalog-contract.md` |
| `field` | Input that caused the refusal, e.g. `budget_bytes`, `case_dir` |
| `unlock` | Concrete action that removes the refusal |
| `detail` | Human-readable specifics |

Used for `AF-CONTEXT-BUDGET-EXHAUSTED` and `AF-CTX-GRAPH-UNAVAILABLE`.
