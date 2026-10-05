# QualityFrontier-v1

§23 the frontier report across declared profiles.

| Field | Meaning |
|---|---|
| `points` | per-profile `FrontierPoint` |
| `pareto_profiles` | non-dominated profiles |
| `source` | the report the frontier was computed from |
| `unresolved` | per-profile unmeasured axes |

Invariant: dominance uses only axes where both points are observed.
