# CostVector/v1

`CostVector/v1` is the measured cost of one emission.

| Field | Meaning |
|---|---|
| `context_bytes` | Serialized bytes of refs or envelope emitted into context |
| `tool_result_bytes` | Bytes returned by an expansion |
| `expansions` | Number of `context expand` calls |
| `cache_hits` | Refs whose object already existed in the ctx store |
| `duration_ms` | Local wall time of the emission |
| `observed_tokens` | Provider tokens only when observed; `null` otherwise |

Bytes are never converted into tokens. `economy stats --transcript` attaches
counted tokens from a host transcript separately.
