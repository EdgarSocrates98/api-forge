# MemoryRetrievalResult/v1

`MemoryRetrievalResult/v1` returns bounded memory records together with the
original query, stale and invalidated counts, unresolved diagnostics and an
explicit ready/degraded/unresolved status.

Result preserves taint count and `MemoryConflict/v1` rows. Applicable trusted
fresh contradictions become `review`; destructive retrieval marks them
`quarantine` and excludes both records.

Canonical schema: `apiforge contract show MemoryRetrievalResult/v1`.
