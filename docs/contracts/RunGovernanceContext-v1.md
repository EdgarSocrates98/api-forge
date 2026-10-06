# RunGovernanceContext/v1

Authoritative local snapshot of the Agent Governor decision for one runtime
run. It is written before optional escalation, debate, shadow work or other
additional calls.

| Field | Meaning |
|---|---|
| `context_id` / `run_id` / `task_id` | Stable identity and ownership |
| `inputs` | Declared profile, risk, budget and available signals |
| `decision` | Conservative ceilings and security clamps |
| `gain` / `stop` | Optional pre-action information-gain and stop decisions |
| `recovery` / `recoveries` / `loop` | `recovery` is the governing scheduler decision for the run's first failure; `recoveries` aggregates every canonical decision (scheduler) plus first-point classifications of post-invocation errors |
| `evidence_refs` | Evidence explicitly available to the decision |
| `unresolved` | Missing signals or unresolved external claims; never silently zeroed |

The receipt is local, append-only through the run store, and does not authorize
cloud, provider, deployment or GitHub mutation.
