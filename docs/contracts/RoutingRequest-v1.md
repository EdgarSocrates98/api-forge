# RoutingRequest/v1

Normalized TaskSpec inputs consumed by risk/complexity classification,
capability eligibility and ranking. In addition to risk, requested
capabilities, evidence, expertise and policy identity, the additive fields are
`task_size`, `dependencies`, `expected_proofs` and `strategy`.

Graph-aware callers may additionally provide `graph_target`, `graph_mode` and
`graph_candidate_refs`. The mapping is caller-supplied node IDs backed by
explicit local graph evidence; capability names are never inferred from graph
properties. `graph_freshness_state` and `graph_evidence` preserve the snapshot
state used by `GraphImpactAssessment/v1`.

Older requests may omit the additive fields. Such requests remain valid and
are classified from the explicit values that are present; no hidden heuristic
fills missing values.
