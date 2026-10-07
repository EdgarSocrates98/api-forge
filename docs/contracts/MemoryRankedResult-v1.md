# MemoryRankedResult/v1

§15 retrieval result: the same bounded filters as `query_memory`, plus a
per-record `MemoryScore` decomposition.

| Field | Meaning |
|---|---|
| `query` | The `MemoryQuery` that produced the ranking |
| `ranked` | `MemoryScore` rows in descending score order, capped at `max_results` |
| `unresolved` | Environment-mismatch and freshness notes, never silent |

`query_memory_scored()` returns this; `query_memory()` uses the same ranking to
order its records, so both surfaces agree on ordering.
