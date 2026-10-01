# CapacityAssessment/v1

Derived capacity gate for a measured `PerformanceRun`. It does not replace
the performance verdict and never converts missing evidence into success.

| Field | Type | Required |
|---|---|---|
| `version` | integer | no |
| `id` | string | yes |
| `produced_by` | string | no |
| `unresolved` | array | no |
| `attributes` | object | no |
| `subject` | string | no |
| `source_run_id` | string | yes |
| `status` | `passed\|failed\|inconclusive` | yes |
| `target_tps` | number|null | no |
| `achieved_tps` | number|null | no |
| `max_safe_tps` | number|null | no |
| `headroom_pct` | number|null | no |
| `blockers` | array | no |
| `evidence` | array | no |

`max_safe_tps` is emitted only when the source run passes and the caller
declares a headroom policy. A failed or incomplete run remains actionable but
cannot be used as a production capacity claim.
