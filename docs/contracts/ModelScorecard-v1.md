# ModelScorecard/v1

Observed model-quality history segmented by provider, model and task class.
Scorecard freshness is a routing constraint for risk-sensitive work.

`fresh` and `mature` records may support normal routing. `cold`/`warming`
records remain usable only for low-risk work; `stale`, `degraded` and
`unresolved` records are ineligible. Missing evidence correctness for a
sensitive or mutating route is unresolved, never a pass.
