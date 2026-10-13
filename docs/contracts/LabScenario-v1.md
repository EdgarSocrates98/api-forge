# LabScenario-v1

One §28 scenario cell inside `LabReport`.

| Field | Meaning |
|---|---|
| `kind` | §28 scenario kind (timeout, retry storm, breaking change, ...) |
| `state` | `covered`/`declared-gap` |
| `fixture`/`eval_id`/`proof` | real coverage pointers |
| `note` | human context for the pointer |
| `gap` | the named gap when `state` is `declared-gap` |

Invariant: `covered` requires at least one real pointer; `declared-gap`
requires a named `gap`; both refuse at load time.
