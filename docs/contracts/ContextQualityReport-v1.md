# ContextQualityReport/v1

Measured quality of one capsule/run selection over recorded uses.

| Field | Meaning |
|---|---|
| `run_id` / `capsule_id` | Run and capsule the metrics describe |
| `refs_total` / `refs_used` / `uses_total` | Selection size, consumed refs and recorded interactions |
| `metrics[]` | All 13 `ContextQualityMetric` rows (closed catalog, no duplicates) |
| `roles[]` | Per-role `RoleContextQuality` rollups |
| `unresolved` | Every metric whose inputs were never recorded, named explicitly |
| `status` | `ready` (all measured), `degraded` (some unresolved) or `unresolved` (none measured) |
