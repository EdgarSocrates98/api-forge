# MemoryEvalReport-v1

§24 the memory corpus verdict across the declared axes.

| Field | Meaning |
|---|---|
| `cases` | per-case `MemoryEvalCaseResult` |
| `totals` | cases/passed |
| `unresolved` | cases that could not run |

Invariant: setup ingress is `persist_candidate` only — seeds pass the same gates as real writes.
