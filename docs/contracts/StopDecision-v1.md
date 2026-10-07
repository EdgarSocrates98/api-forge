# StopDecision/v1

§25 explicit STOP. The run does not continue merely because budget
remains: it continues when `expected_gain > threshold` or a mandatory
requirement is unmet.

| Field | Meaning |
|---|---|
| `decision` | `continue` or `stop` |
| `expected_gain` | The scored gain; `null` when unmeasurable |
| `threshold` | The declared bar; the comparison is strict (`>`) |
| `mandatory_requirement` | A requirement that overrides the gain check |
| `code` | `AF-GOV-GAIN-UNRESOLVED` or `AF-GOV-STOP-LOW-GAIN` when stopping |

An unmeasurable gain fails closed: STOP with `AF-GOV-GAIN-UNRESOLVED`,
because continuing cannot be justified.
