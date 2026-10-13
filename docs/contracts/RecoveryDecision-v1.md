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

## Execution (supervisor)

Decisions are not labels — the supervisor executes each terminal decision
exactly once after the invocation pass and persists a
[`RecoveryReceipt/v1`](RecoveryReceipt-v1.md) per decision:

| Decision | Owner | Executed action |
|---|---|---|
| `retry` | supervisor (post-invocation) or scheduler | a single accounted `recovery` call; scheduler-internal retries never reach the supervisor |
| `replan` | supervisor | re-route with failed capabilities excluded → new `RoutingDecision`/`RoutingPlan` → new strategy fingerprint + loop check → `ControlPlane.add_steps` → bounded invocation (refusals: `AF-GOV-RECOVERY-REPLAN-REFUSED`) |
| `fallback` | supervisor | next kind-compatible name from the declared `RoutingDecision.fallback_order`, bounded by the plan's `max_fallbacks` (refusals: `AF-GOV-RECOVERY-NO-FALLBACK`) |
| `escalate` | human | raises the `recovery_escalation` gate reason; the runtime policy decides whether it opens the human gate (`AF-GOV-RECOVERY-ESCALATION`) |
| `stop` | none | terminal — no further calls for that failure chain |

Depth is bounded at one: a recovery-invoked invocation that fails records its
own decision and a `skipped` receipt (`AF-GOV-RECOVERY-DEPTH`) — the executor
never spawns a second recovery pass.
