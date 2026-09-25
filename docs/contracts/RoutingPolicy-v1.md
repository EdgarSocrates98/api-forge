# RoutingPolicy/v1

Bounded routing policy defining objective order, security gate, unknown-signal
behavior, tie-breaker, eval-gated scorecard updates and the local
`risk_complexity` policy.

`risk_complexity.policy_version` versions the ordered predicates and effects
used to produce `RiskComplexityAssessment/v1`. MVP predicates are explicit:
missing evidence, missing expertise, task size, declared dependencies,
expected proofs and verification-oriented strategy. Safety risks are explicit
overrides; scorecards and graph impact are not consulted.

The effects map each complexity level to objective order, verification depth
and required review roles. Malformed or incomplete policy data is refused with
`AF-RUNTIME-POLICY`; no partial/default rule set may be used silently.
