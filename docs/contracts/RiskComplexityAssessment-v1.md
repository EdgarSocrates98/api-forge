# RiskComplexityAssessment/v1

`RiskComplexityAssessment/v1` is the immutable, deterministic explanation of
how explicit task risk and complexity inputs affect routing. It is produced by
the local policy compiler before candidate ranking and is attached to
`RoutingDecision/v1`.

| Field | Meaning |
|---|---|
| `assessment_id` | Stable hash of task revision, policy version, normalized inputs, matched factors and unresolved state |
| `task_id` / `revision` | Source TaskSpec identity |
| `policy_id` / `policy_version` | Routing policy and risk/complexity policy provenance |
| `risk` | Explicit TaskRisk value supplied by the task |
| `complexity` | `simple`, `moderate`, `complex` or `critical` |
| `factors` | Ordered, unique local rule/risk factors that affected classification |
| `objective_order` | Routing objective order selected for ranking |
| `verification_depth` | `standard`, `elevated` or `strict` |
| `required_roles` | Review roles required by policy: reviewer, critic and/or referee |
| `gate_state` | `open`, `review` or `blocked`; unresolved inputs block classification |
| `evidence` | Evidence refs available to the classifier |
| `unresolved` | Preserved gaps and actionable `AF-*` diagnostics |

The classifier reads only explicit local inputs and versioned YAML policy. It
does not call a model/provider, network, live database or external mutation
boundary. Historical scorecards and graph impact are not MVP inputs; B and C
may add versioned evidence fields in future contracts.

Missing required evidence or expertise remains unresolved and cannot become a
confident fallback. Every refusal preserves an `AF-*` code, rejected `field`
and safe `unlock` according to the project catalog contract.

The contract is frozen, closed and versioned. Existing routing payloads remain
valid because `RoutingDecision/v1.risk_complexity` is additive and optional.
