# MemoryGateResult/v1

Outcome of the §14 gate pipeline for one `MemoryCandidate`, produced by
`evaluate_gates()` before any store mutation.

| Field | Meaning |
|---|---|
| `candidate_id` | The evaluated candidate |
| `verdict` | `persist`, `quarantine` or `reject` |
| `gates_passed` / `gates_failed` | Ordered subset of `scope`, `origin`, `evidence`, `outcome`, `freshness`, `trust` |
| `quarantine_reasons` | Why the candidate parked (only on `quarantine`) |
| `code` / `field` / `unlock` | `AF-MEMORY-*` refusal triad |

Hard violations (scope, untrusted/model origin, missing persistent evidence,
expired payload) reject with the historical codes. Borderline trust below the
policy minimum quarantines — reviewable data, never silently dropped.
