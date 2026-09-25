# RoutingRequest/v1

Normalized TaskSpec inputs consumed by risk/complexity classification,
capability eligibility and ranking. In addition to risk, requested
capabilities, evidence, expertise and policy identity, the additive fields are
`task_size`, `dependencies`, `expected_proofs` and `strategy`.

Older requests may omit the additive fields. Such requests remain valid and
are classified from the explicit values that are present; no hidden heuristic
fills missing values.
