# ToolBenchmark/v1

§43 aggregated cost for one tool over declared samples.

| Field | Meaning |
|---|---|
| `tool` | sampled tool |
| `samples` | successful invocations counted |
| `median_bytes`/`p95_bytes` | measured response sizes |
| `median_tokens_est`/`p95_tokens_est` | chars/4 estimate — always `estimated` |
| `usefulness` | `met`/`missed`/`unresolved` vs declared `max_bytes` |
| `basis` | `estimated` — fixed |

Invariant: token counts are heuristic estimates, never presented as
provider-counted usage.
