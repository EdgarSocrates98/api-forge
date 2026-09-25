# ScorecardShadowEvaluation/v1

Offline, read-only comparison between the static route produced by the
existing objective ranking and the adaptive route produced by
`ScorecardRoutingAssessment/v1`.

| Field | Meaning |
|---|---|
| `evaluation_id` | Stable hash of both route proposals and their evidence |
| `assessment_id` | Scorecard assessment used for the adaptive proposal |
| `baseline_policy_version` | Policy identity for the static route |
| `adaptive_policy_version` | Scorecard adaptation policy identity |
| `baseline_order` / `adaptive_order` | Candidate order in each proposal |
| `baseline_selected` / `adaptive_selected` | First candidate in each proposal, if any |
| `selected_changed` | Whether the proposed primary candidate differs |
| `changed_candidates` | Candidates whose positions differ between proposals |
| `comparison` | `unchanged`, `reordered` or `challenger-selected` |
| `executed` | Always `false`; this contract never invokes a capability |
| `evidence` / `unresolved` | Scorecard provenance and unresolved diagnostics |
| `limitations` | Explicit offline and no-invocation limitations |

The evaluation is persisted inside `RoutingDecision/v1` and as the local
`shadow-evaluation.json` run artifact. The `shadow` evolution mode records this
comparison and stops before capability invocation. It does not claim live
quality, latency, cost or provider behavior.
