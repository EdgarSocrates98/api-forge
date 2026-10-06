# ControlPlaneRoute/v1

§28 a decision route under lifecycle governance. Declared in
`rules/control_plane.yaml`; the effective mode overlays the latest row in
`control-plane/modes.jsonl` — the declared file is never mutated.

| Field | Meaning |
|---|---|
| `route` | The route name (`model_routing`, `tool_authorization`, …) |
| `mode` | `shadow` → `assisted` → `active`; the latest overlay wins |
| `candidate` / `legacy` | The new and authoritative decision systems |
| `fallback_route` | §32 destination when the active route degrades; `null` marks a terminal route whose degradation refuses |
| `promoted_at` / `promotion_approval_id` | Stamp of the last transition and the gate that authorized it |
