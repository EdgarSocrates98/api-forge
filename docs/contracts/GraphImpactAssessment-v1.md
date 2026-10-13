# GraphImpactAssessment/v1

`GraphImpactAssessment/v1` is the canonical immutable result of one local graph
assessment. Routing, the execution plan and user-facing projections consume this
stored value; they do not traverse the graph independently.

| Field | Meaning |
|---|---|
| `assessment_id` | Stable identity of target, mode, policy, snapshot, bounds, evidence and result |
| `target_id` / `target_kind` | Explicit graph target and its closed `NodeKind`, when present |
| `mode` | `direct`, `transitive` or `all` |
| `policy_version` | Graph policy provenance |
| `graph_snapshot` | Optional `GraphExport/v1` hashes and counts |
| `coverage` | `complete`, `partial`, `missing` or `unresolved` |
| `freshness_state` | `fresh`, `stale`, `unresolved` or `unknown` |
| `impact_band` | `none`, `explicit`, `bounded` or `unresolved` |
| `impacted_nodes` | Ordered typed nodes with depth, explicit edge references and source evidence |
| `candidate_impacts` | Candidate-to-node mapping and explicit selection explanation |
| `gate_state` / `verification_depth` | Additive graph policy effect |
| `required_roles` / `selection_effect` | Review and candidate-selection effects |
| `evidence` / `unresolved` / `limitations` | Complete provenance and bounded traversal gaps |

Traversal follows only explicit reverse edges (`to_id` to `from_id`) and is
bounded by policy depth, node and edge limits. The canonical order is lexical by
depth and node ID; evidence, candidates, unresolved values and limitations are
lexically ordered. Cycles, stale snapshots, missing targets and budget cutoffs
remain visible. No graph inference, provider call, network request, database
access or graph mutation is allowed.
