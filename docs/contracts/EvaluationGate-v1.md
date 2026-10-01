# EvaluationGate/v1

`EvaluationGate/v1` is `apiforge evals gate --baseline A --candidate B`.

| Field | Meaning |
|---|---|
| `decision` | `ship` or `reject` |
| `quality_regressions` / `safety_regressions` / `holdout_regressions` | `case@profile` rows that regressed |
| `mutation_regression` | Fewer mutants detected (or fewer mutants) than the baseline |
| `max_quality_regression` | Tolerated quality regressions (default 0); safety is never tolerated |
| `calls_delta` | Mean calls per profile, candidate minus baseline — reported, never an excuse |
| `reasons` | Why the decision was taken |
