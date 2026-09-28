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
| `mode` | `paired_ab` (default: the challenger receives the primary's context) or `capability_eval` (TaskSpec input `shadow_mode=capability_eval`: the challenger receives its own role and expertise context) |

The shadow call is accounted by the ControlPlane (`calls_by_kind.shadow`), so `calls_used` and `economy_checkpoint.json` match real adapter invocations; when the budget is spent the shadow is skipped with `AF-BUDGET-EXHAUSTED`.
