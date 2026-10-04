# RunInspection/v1

§53–§54 the full single-run AgentOps report — the JSON projection of
`apiforge agentops inspect`.

| Field | Meaning |
|---|---|
| `run_id` | Run id joined across the local ledgers |
| `task_id` | Declared task when recorded; `null` otherwise |
| `profile`/`risk` | Declared run profile/risk; never inferred |
| `sections` | `run`, `agents`, `context`, `memory`, `tools`, `models`, `evidence`, `security` — sections never drop silently; absent data becomes `unresolved` metrics |
| `waste` | §56 findings from the declared detectors |
| `decision_path` | Ordered decision-gate ids for the run |
| `unresolved` | Every section or metric that stayed unresolved, with the reason |

Invariant: no metric, section or finding is fabricated — missing source data is
named in `unresolved`, not filled with zeroes.
