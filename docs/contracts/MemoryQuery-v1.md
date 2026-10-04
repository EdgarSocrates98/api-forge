# MemoryQuery/v1

`MemoryQuery/v1` is an explicit bounded retrieval request. It carries terms,
scopes, environment fingerprint, minimum trust, freshness clock, invalidation
visibility and a maximum result count. Missing clocks or environment mismatch
remain visible as unresolved retrieval state.

Canonical schema: `apiforge contract show MemoryQuery/v1`.
