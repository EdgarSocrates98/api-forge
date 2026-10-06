# RoleContextTelemetry/v1

Measured per-role context counters: what each role loaded, expanded, cited,
spent in tokens, drew from evidence, hit in cache, duplicated and left unused.

| Field | Meaning |
|---|---|
| `run_id` / `role` / `capability` | Run, role and the capability it served |
| `refs_assigned` / `refs_expanded` / `refs_cited` | Delivery and consumption counters |
| `context_bytes` / `tokens` / `tokens_basis` | Bytes assigned and observed tokens when recorded |
| `evidence_refs` | Used refs of evidence kinds (contract, schema, policy, knowledge, test) |
| `cache_hits` / `duplicates` / `unused_refs` | Cache, dedup and the assigned-but-never-used estimate |
