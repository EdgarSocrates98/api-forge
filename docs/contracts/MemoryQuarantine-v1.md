# MemoryQuarantine/v1

A row in the append-only `quarantine.jsonl` log — either a pending quarantine
or its resolution (step11 §14).

| Field | Meaning |
|---|---|
| `quarantine_id` | `quarantine:<sha16>`, deterministic per candidate_id |
| `candidate_id` / `memory_id` | The parked candidate and its would-be record id |
| `state` | `quarantined` (pending) or `released` (resolved) |
| `reasons` | Gate reasons that parked the candidate |
| `verdict` | On release rows: `persisted` or `rejected` |
| `resolved_by` | The human reviewer on release rows |

Quarantined candidates are invisible to `query_memory` — they live in a
separate log, and only `review_quarantine()` may release them. Release to
`persist` re-runs the full gate pipeline; a reviewer cannot bypass gates.
