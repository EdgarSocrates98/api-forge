# TokenAccounting/v1

Usage accounting for one unit of provider work (step11 §20). One row is
exactly one basis — `observed`, `estimated` or `unresolved` — and the
bases are never mixed inside a sum.

| Field | Meaning |
|---|---|
| `basis` | `observed` (provider transcript/report), `estimated` (declared method), or `unresolved` (usage unknown) |
| `input_tokens` / `output_tokens` | Standard provider usage fields |
| `cached_input_tokens` / `cache_creation_tokens` | Cache-read and cache-write tokens when the provider reports them |
| `reasoning_tokens` | Reasoning/thinking tokens when the provider reports them |
| `model` | Provider model id when known |
| `source` | Where the row came from (`transcript:<path>`, `estimate`, …) |
| `estimation_method` | Mandatory when `basis=estimated` (e.g. `bytes/4`) |

Invariant — NEVER MIX: `unresolved` rows reject every token count;
`estimated` rows require a declared `estimation_method`; `total()` sums
present fields only, so a missing field contributes zero, never a guess.
