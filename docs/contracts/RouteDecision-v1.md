# RouteDecision/v1

Which decision stream governs one evaluation, per the route's lifecycle
mode.

| Field | Meaning |
|---|---|
| `mode` | The effective mode at evaluation time |
| `governing` | `legacy` (shadow/assisted), `candidate` (active, no trigger) or `none` (fallback fired) |
| `recommendation` | In `assisted`: the candidate's proposal; legacy stays authoritative |
| `shadow` | `true` when a `ShadowRecord` was appended |
| `fallback` | The `FallbackDecision` when a §32 trigger fired |
