# AgenticRuntime/v1

Frozen, closed (`extra: forbid`) contracts for a provider-neutral agentic run.
The runtime envelope is bound to one sealed `TaskSpec` revision and does not
replace TaskSpec, Debate or VerificationRecord.

| Contract | Purpose |
|---|---|
| `AgenticRun/v1` | Run state, task/revision binding, artifacts, decisions, gaps and terminal brief status. |
| `AgenticPolicy/v1` | Budgets, concurrency, risk triggers, approval gates and adapter selection. |
| `AgentInvocation/v1` | One agent/adapter attempt, dependencies, usage, duration and error. |
| `AgentArtifact/v1` | Typed, hashed structured output with evidence, risks and unresolved claims. |
| `HandoffRecord/v1` | Context and evidence transferred between agent roles. |
| `DecisionRecord/v1` | Resolved/unresolved decision with options, evidence, dissent and referee. |
| `ApprovalGate/v1` | Human approval required for critical actions or unresolved risk. |
| `TrajectoryEvent/v1` | Append-only auditable event for runtime transitions and tool activity. |

Canonical invariants:

- `version` is a literal contract version; incompatible changes require v2.
- Extra fields are rejected and instances are frozen.
- A run references one TaskSpec revision and cannot execute a stale plan.
- `DONE` is derived by `OutcomeBrief` only after independent verification and
  clean holdout/mutation evidence.
- `unresolved`, `inconclusive`, `blocked` and `not_observed` remain distinct.
- Provider-native responses are not canonical until normalized into an
  `AgentArtifact` and validated against its declared schema.
- External mutation requires policy permission and an `ApprovalGate`; the
  default `local-ci-safe` policy denies it.
