# ShadowDecision/v1

`ShadowDecision/v1` records the bounded challenger shadow of a runtime run.

| Field | Meaning |
|---|---|
| `share` | `envelope.shadow_share` of the effective profile |
| `sampled` | `sha256(run_id)` bucket below `share × 10000` — replays decide the same |
| `executed` / `challenger` / `calls` | Whether the first planned challenger ran, and how many calls it used |
| `reason` | `shadow disabled`, `no challenger planned`, `run not sampled`, `AF-ECONOMY-SHADOW-BUDGET: ...` or `sampled within share` |
| `agreement` | Challenger recommendation equals the primary's (null without a primary artifact) |

The shadow artifact is stored as `shadow-<capability>.json`; it never enters
the run's artifacts, gaps or final status.
