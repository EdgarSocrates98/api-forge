# ContextSufficiencyResult/v1

Minimum-sufficient-context decision: what a capsule can drop without quality
loss, under the declared `strict` / `evidence` / `permissive` gate.

| Field | Meaning |
|---|---|
| `kept_refs` / `pruned_refs` / `pruned_bytes` | The deterministic prune fixpoint (consumed + required, plus evidence kinds unless `permissive`) |
| `gate` | The gate applied |
| `metrics_before` / `metrics_after` | Full metric snapshots on both sides of the prune |
| `sufficient` | True only when required refs are present and gated recalls never regress |
| `unresolved` | Missing required refs, unmeasurable-after-prune recalls, already-minimal selections |
