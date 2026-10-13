# AgenticDoctorReport-v1

Cross-plane agentic health emitted by `apiforge doctor --agentic`.

| Field | Meaning |
|---|---|
| `sections` | per-plane `AgenticDoctorSection` rows |
| `findings` | flattened `DoctorFinding` rows across sections |
| `unresolved` | planes with no observable persisted state, named |
| `status` | `ok`/`attention`/`unresolved` |

Invariant: read-only and local — no provider, host or network call;
`unresolved` is a plane state, never an implied pass or failure.
