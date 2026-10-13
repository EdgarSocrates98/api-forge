# WasteReport/v1

§56–§57 detector output for one run — the JSON projection of
`apiforge agentops waste`.

| Field | Meaning |
|---|---|
| `run_id` | Run id inspected |
| `findings` | `WasteFinding` rows, deterministically ordered |
| `unresolved` | Detectors that could not run and why |

Invariant: every finding carries `evidence` in
`observed`/`estimated`/`hypothesis`; detectors that lacked a prerequisite
(undeclared risk, absent ledger class) are listed in `unresolved`, not skipped
silently.
