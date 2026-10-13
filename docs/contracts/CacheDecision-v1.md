# CacheDecision/v1

`CacheDecision/v1` records what the store decided for one lookup — a reuse is
never silent.

| Field | Meaning |
|---|---|
| `layer` / `key` / `subject` | The entry looked up |
| `state` | `miss`, `fresh`, `stale_harmless`, `stale_critical`, `invalidated` or `corrupt` |
| `action` | `reuse`, `reuse_warn`, `recompute` or `invalidate` |
| `tier` | `local` or `shared` when an entry was found |
| `reason` | Probe that decided, e.g. `dependency proj/app/models.py:9-13 changed` |
| `warnings` | Set for `reuse_warn` (expired entry on a `warn` layer) |
