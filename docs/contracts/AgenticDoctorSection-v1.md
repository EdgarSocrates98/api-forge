# AgenticDoctorSection-v1

Health for one declared plane inside `AgenticDoctorReport`.

| Field | Meaning |
|---|---|
| `plane` | plane name (case/memory/trust/telemetry/evals/sdd/mcp/economy) |
| `state` | `ok`/`attention`/`unresolved` |
| `checks` | executed check ids |
| `findings` | `DoctorFinding` rows with unlocks |
| `unresolved` | why the plane cannot be judged |

Invariant: a missing artifact yields `unresolved` plus the reason — never
a silent zero or a fabricated verdict.
