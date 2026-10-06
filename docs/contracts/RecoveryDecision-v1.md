# RecoveryDecision/v1

§26 governed recovery for one classified failure. The failure-class
vocabulary is closed: unknown classes refuse
`AF-GOV-FAILURE-CLASS-UNKNOWN`.

| Field | Meaning |
|---|---|
| `failure_class` | One of the §26 classes (`missing_evidence` … `deterministic_conflict`) |
| `decision` | `retry`, `replan`, `fallback`, `escalate` or `stop` — the ladder step |
| `attempt` / `max_attempts` | Where in the ladder this attempt sits |
| `code` | `AF-GOV-RECOVERY-UNDECLARED` (class valid but absent from policy) or `AF-GOV-RECOVERY-EXHAUSTED` (cap reached; terminal `escalate`/`stop` fires) |
| `unresolved` | Named gaps, never silent |

The scheduler classifies each worker failure (`governance.recovery.
classify_failure`, the single classification surface) and records
`RecoveryDecision` before deciding whether another attempt may start.
`InvocationResult.recovery` is the canonical decision for that failure — the
supervisor consumes and aggregates it, and only classifies errors that never
passed through the scheduler (post-invocation payload gaps, budget-blocked
fallbacks). `retry` alone permits a retry; `replan`, `fallback`, `escalate`
and `stop` terminate the local retry loop for an upper runtime layer to
handle. Runtime `max_retries` remains a hard ceiling and is reported as
`AF-GOV-RECOVERY-EXHAUSTED`.
