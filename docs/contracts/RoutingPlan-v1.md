# RoutingPlan/v1

`RoutingPlan/v1` is the additive execution contract derived from
`RoutingDecision/v1`. It makes execution roles explicit while preserving the
legacy `routing.json` decision and `fallback_order` fields.

| Field | Meaning |
|---|---|
| `plan_id` | Stable hash of the decision, policy and role assignment |
| `decision_id` | Source `RoutingDecision/v1` identifier |
| `primary` | First eligible capability, if one exists |
| `fallbacks` | Ordered, bounded candidates activated only by failover policy |
| `parallel` | Independent candidates run in the parallel-review mode |
| `reviewers` | Capabilities with reviewer role |
| `critic` / `referee` | Optional explicit critique and arbitration roles |
| `execution_mode` | `parallel_review` or `sequential_failover` |
| `max_fallbacks` | Deterministic fallback budget |
| `assessment_id` | Source `RiskComplexityAssessment/v1`, when present |
| `complexity` / `verification_depth` | Policy effects selected by the assessment |
| `required_roles` | Review roles requested by the assessment |
| `gate_state` | `open`, `review` or `blocked` policy state |
| `evidence` / `unresolved` | Provenance and gaps retained from routing |

Roles cannot contain duplicate capabilities. Fallbacks cannot exceed the
declared budget. The contract is local, offline-first, frozen and versioned;
it does not execute an agent, call a provider or mutate host files.
